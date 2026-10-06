/**
 * Page image loading through the EXISTING resource channel (Task AC2:
 * "Viewer consumes the existing resourceChannel"). One fresh issue per
 * mount (never reuse opaque references), chunked fetch assembled into a
 * Blob, surfaced as an object URL for <img>.
 *
 * Production gap registered in the Task: page->resource catalogization does
 * not exist on the production face yet (only the acceptance bridge seeds
 * entries), so the caller must supply the resource id + revision explicitly.
 */

import { ResourceChannelClient, TypedChannelError } from "../resourceChannel/client";

export async function loadPageImageUrl(
  client: ResourceChannelClient,
  resourceId: string,
  revision: string,
): Promise<string> {
  if (!resourceId || !revision) {
    throw new TypedChannelError("REF_MALFORMED");
  }
  const issued = await client.issue(resourceId, revision);
  const blob = await client.fetchAll(issued.url, issued.size);
  return URL.createObjectURL(blob);
}
