/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Artist } from "../models/Artist";
import type { ArtistIndex } from "../models/ArtistIndex";
import type { Labels } from "../models/Labels";

import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";

export class DefaultService {
  /**
   * Fake Route
   * @returns Labels Successful Response
   * @throws ApiError
   */
  public static getLabels(): CancelablePromise<Labels> {
    return __request(OpenAPI, {
      method: "GET",
      url: "./api/labels.json",
    });
  }

  /**
   * Fake Route
   * @returns ArtistIndex Successful Response
   * @throws ApiError
   */
  public static getArtists(): CancelablePromise<ArtistIndex> {
    return __request(OpenAPI, {
      method: "GET",
      url: "./api/artistIndex.json",
    });
  }

  /**
   * Fake Get Artist Route
   * @param artistId
   * @returns Artist Successful Response
   * @throws ApiError
   */
  public static getArtist(artistId: string): CancelablePromise<Artist> {
    return __request(OpenAPI, {
      method: "GET",
      url: "./api/artists/{artist_id}.json",
      path: {
        artist_id: artistId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
