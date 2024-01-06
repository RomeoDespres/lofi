/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
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
}
