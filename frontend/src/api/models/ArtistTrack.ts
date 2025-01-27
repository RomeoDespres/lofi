/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ArtistTrackAlbum } from "./ArtistTrackAlbum";
import type { ArtistTrackArtist } from "./ArtistTrackArtist";

export type ArtistTrack = {
  album: ArtistTrackAlbum;
  artists: Array<ArtistTrackArtist>;
  id: string;
  isrc: string;
  name: string;
};
