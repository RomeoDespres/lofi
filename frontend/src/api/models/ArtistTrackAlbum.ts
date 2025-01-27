/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ArtistTrackArtist } from "./ArtistTrackArtist";
import type { BasicLabel } from "./BasicLabel";

export type ArtistTrackAlbum = {
  artists: Array<ArtistTrackArtist>;
  id: string;
  imageUrlS: string | null;
  label: BasicLabel;
  name: string;
  releaseDate: string;
};
