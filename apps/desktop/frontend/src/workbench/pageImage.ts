/**
 * Page image loading through the EXISTING resource channel (Task AC2:
 * "Viewer consumes the existing resourceChannel"). One fresh issue per
 * mount (never reuse opaque references), chunked fetch assembled into a
 * Blob, surfaced as an object URL for <img>.
 *
 * The historical production gap is closed (M2-PAGE-RESOURCE-RESOLVE-1):
 * `resolve_page_resource` maps a page_id to its managed-original catalog
 * key on the production face, so the Workbench feeds this loader the
 * resolved id + revision without rendering either value in the UI.
 */

import { ResourceChannelClient, TypedChannelError } from "../resourceChannel/client";

export async function loadPageImageUrl(
  client: ResourceChannelClient,
  resourceId: string,
  revision: string,
  onProgress?: (loadedChunks: number, totalChunks: number) => void,
): Promise<string> {
  if (!resourceId || !revision) {
    throw new TypedChannelError("REF_MALFORMED");
  }
  const issued = await client.issue(resourceId, revision);
  const blob = await client.fetchAll(issued.url, issued.size, undefined, onProgress);
  return URL.createObjectURL(blob);
}
