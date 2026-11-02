use std::sync::atomic::{compiler_fence, Ordering};

pub(crate) enum PromptResult {
    Stored,
    Cancelled,
}

pub(crate) fn prompt_and_store(target: &str) -> Result<PromptResult, ()> {
    #[cfg(windows)]
    {
        windows::prompt_and_store(target)
    }
    #[cfg(not(windows))]
    {
        let _ = target;
        Err(())
    }
}

pub(crate) fn delete(target: &str) -> Result<(), ()> {
    #[cfg(windows)]
    {
        windows::delete(target)
    }
    #[cfg(not(windows))]
    {
        let _ = target;
        Err(())
    }
}

struct SecretWide<const N: usize>([u16; N]);

impl<const N: usize> Drop for SecretWide<N> {
    fn drop(&mut self) {
        for unit in &mut self.0 {
            unsafe { std::ptr::write_volatile(unit, 0) };
        }
        compiler_fence(Ordering::SeqCst);
    }
}

#[cfg(windows)]
mod windows {
    use super::{PromptResult, SecretWide};
    use std::{ffi::c_void, mem::size_of, ptr};

    const CRED_TYPE_GENERIC: u32 = 1;
    const CRED_PERSIST_LOCAL_MACHINE: u32 = 2;
    const ERROR_CANCELLED: u32 = 1223;
    const ERROR_NOT_FOUND: i32 = 1168;
    const CREDUI_FLAGS_DO_NOT_PERSIST: u32 = 0x0000_0002;
    const CREDUI_FLAGS_EXCLUDE_CERTIFICATES: u32 = 0x0000_0008;
    const CREDUI_FLAGS_ALWAYS_SHOW_UI: u32 = 0x0000_0080;
    const CREDUI_FLAGS_PASSWORD_ONLY_OK: u32 = 0x0000_0200;
    const CREDUI_FLAGS_GENERIC_CREDENTIALS: u32 = 0x0004_0000;
    // shortcut: CredUI accepts at most 256 UTF-16 units here; replace only with an approved secure input API that supports larger values.
    const CREDUI_MAX_PASSWORD: usize = 256;
    const CREDUI_MAX_USERNAME: usize = 513;

    #[repr(C)]
    struct FileTime {
        low_date_time: u32,
        high_date_time: u32,
    }

    #[repr(C)]
    struct CredentialW {
        flags: u32,
        type_: u32,
        target_name: *mut u16,
        comment: *mut u16,
        last_written: FileTime,
        credential_blob_size: u32,
        credential_blob: *mut u8,
        persist: u32,
        attribute_count: u32,
        attributes: *mut c_void,
        target_alias: *mut u16,
        user_name: *mut u16,
    }

    #[repr(C)]
    struct CredUiInfoW {
        cb_size: u32,
        hwnd_parent: *mut c_void,
        message_text: *const u16,
        caption_text: *const u16,
        banner: *mut c_void,
    }

    #[link(name = "advapi32")]
    unsafe extern "system" {
        fn CredReadW(
            target: *const u16,
            type_: u32,
            flags: u32,
            credential: *mut *mut CredentialW,
        ) -> i32;
        fn CredWriteW(credential: *const CredentialW, flags: u32) -> i32;
        fn CredDeleteW(target: *const u16, type_: u32, flags: u32) -> i32;
        fn CredFree(buffer: *mut c_void);
    }

    #[link(name = "credui")]
    unsafe extern "system" {
        fn CredUIPromptForCredentialsW(
            info: *const CredUiInfoW,
            target: *const u16,
            context: *mut c_void,
            auth_error: u32,
            user_name: *mut u16,
            user_name_size: u32,
            password: *mut u16,
            password_size: u32,
            save: *mut i32,
            flags: u32,
        ) -> u32;
    }

    fn exists(target: &[u16]) -> Result<bool, ()> {
        let mut credential = ptr::null_mut();
        let ok = unsafe { CredReadW(target.as_ptr(), CRED_TYPE_GENERIC, 0, &mut credential) };
        if ok != 0 {
            unsafe { CredFree(credential.cast()) };
            Ok(true)
        } else if std::io::Error::last_os_error().raw_os_error() == Some(ERROR_NOT_FOUND) {
            Ok(false)
        } else {
            Err(())
        }
    }

    fn write(target: &[u16], secret: &[u16]) -> Result<(), ()> {
        let blob_size =
            u32::try_from(secret.len().checked_mul(size_of::<u16>()).ok_or(())?).map_err(|_| ())?;
        let credential = CredentialW {
            flags: 0,
            type_: CRED_TYPE_GENERIC,
            target_name: target.as_ptr() as *mut u16,
            comment: ptr::null_mut(),
            last_written: FileTime {
                low_date_time: 0,
                high_date_time: 0,
            },
            credential_blob_size: blob_size,
            credential_blob: if secret.is_empty() {
                ptr::null_mut()
            } else {
                secret.as_ptr() as *mut u8
            },
            persist: CRED_PERSIST_LOCAL_MACHINE,
            attribute_count: 0,
            attributes: ptr::null_mut(),
            target_alias: ptr::null_mut(),
            user_name: ptr::null_mut(),
        };
        (unsafe { CredWriteW(&credential, 0) } != 0)
            .then_some(())
            .ok_or(())
    }

    pub(super) fn prompt_and_store(target: &str) -> Result<PromptResult, ()> {
        let target: Vec<u16> = target.encode_utf16().chain(std::iter::once(0)).collect();
        if exists(&target)? {
            return Err(());
        }

        let caption: Vec<u16> = "New Manga"
            .encode_utf16()
            .chain(std::iter::once(0))
            .collect();
        let message: Vec<u16> = "Enter the credential in this Windows dialog. It will be stored in Windows Credential Manager."
            .encode_utf16()
            .chain(std::iter::once(0))
            .collect();
        let info = CredUiInfoW {
            cb_size: size_of::<CredUiInfoW>() as u32,
            hwnd_parent: ptr::null_mut(),
            message_text: message.as_ptr(),
            caption_text: caption.as_ptr(),
            banner: ptr::null_mut(),
        };
        let mut user_name = SecretWide([0u16; CREDUI_MAX_USERNAME]);
        let mut password = SecretWide([0u16; CREDUI_MAX_PASSWORD]);
        let status = unsafe {
            CredUIPromptForCredentialsW(
                &info,
                target.as_ptr(),
                ptr::null_mut(),
                0,
                user_name.0.as_mut_ptr(),
                user_name.0.len() as u32,
                password.0.as_mut_ptr(),
                password.0.len() as u32,
                ptr::null_mut(),
                CREDUI_FLAGS_DO_NOT_PERSIST
                    | CREDUI_FLAGS_EXCLUDE_CERTIFICATES
                    | CREDUI_FLAGS_ALWAYS_SHOW_UI
                    | CREDUI_FLAGS_PASSWORD_ONLY_OK
                    | CREDUI_FLAGS_GENERIC_CREDENTIALS,
            )
        };
        if status == ERROR_CANCELLED {
            return Ok(PromptResult::Cancelled);
        }
        if status != 0 {
            return Err(());
        }
        let length = password.0.iter().position(|unit| *unit == 0).ok_or(())?;
        write(&target, &password.0[..length])?;
        Ok(PromptResult::Stored)
    }

    pub(super) fn delete(target: &str) -> Result<(), ()> {
        let target: Vec<u16> = target.encode_utf16().chain(std::iter::once(0)).collect();
        let ok = unsafe { CredDeleteW(target.as_ptr(), CRED_TYPE_GENERIC, 0) };
        (ok != 0).then_some(()).ok_or(())
    }

    #[cfg(test)]
    mod tests {
        use super::*;
        use rand::RngCore;

        struct Cleanup {
            target: Vec<u16>,
            armed: bool,
        }

        impl Drop for Cleanup {
            fn drop(&mut self) {
                if self.armed {
                    let _ = delete(&String::from_utf16_lossy(
                        &self.target[..self.target.len().saturating_sub(1)],
                    ));
                }
            }
        }

        #[test]
        fn credential_manager_round_trips_and_deletes_a_temporary_value() {
            let mut nonce = [0u8; 16];
            rand::rngs::OsRng.try_fill_bytes(&mut nonce).unwrap();
            let suffix = nonce
                .iter()
                .map(|byte| format!("{byte:02x}"))
                .collect::<String>();
            let target = format!("NewManga/provider/p15-host-2-smoke/{suffix}");
            let target_wide: Vec<u16> = target.encode_utf16().chain(std::iter::once(0)).collect();
            let mut cleanup = Cleanup {
                target: target_wide.clone(),
                armed: false,
            };
            assert!(
                !exists(&target_wide).unwrap(),
                "temporary credential ref must be new"
            );
            let mut marker = SecretWide([0u16; 6]);
            marker.0[..5].copy_from_slice(&[0x50, 0x31, 0x35, 0x2d, 0x32]);
            write(&target_wide, &marker.0[..5]).unwrap();
            cleanup.armed = true;

            let mut stored = ptr::null_mut();
            assert_ne!(
                unsafe { CredReadW(target_wide.as_ptr(), CRED_TYPE_GENERIC, 0, &mut stored) },
                0,
                "temporary Credential Manager value must be readable"
            );
            let credential = unsafe { &*stored };
            let bytes = unsafe {
                std::slice::from_raw_parts(
                    credential.credential_blob,
                    credential.credential_blob_size as usize,
                )
            };
            let expected = [0x50u8, 0, 0x31, 0, 0x35, 0, 0x2d, 0, 0x32, 0];
            assert!(
                bytes == expected,
                "credential UTF-16LE bytes must round-trip"
            );
            unsafe { CredFree(stored.cast()) };
            delete(&target).unwrap();
            cleanup.armed = false;
            assert!(!exists(&target_wide).unwrap());
        }
    }
}
