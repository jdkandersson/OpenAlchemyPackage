/**
 * This file was auto-generated by openapi-typescript.
 * Do not make direct changes to the file.
 */

export interface paths {
  '/specs': {
    get: operations['library.specs.list_'];
  };
  '/specs/{spec_id}': {
    get: operations['library.specs.get'];
    put: operations['library.specs.put'];
    delete: operations['library.specs.delete'];
  };
  '/specs/{spec_id}/versions': {
    get: operations['library.specs.versions.list_'];
  };
  '/specs/{spec_id}/versions/{version}': {
    get: operations['library.specs.versions.get'];
    put: operations['library.specs.versions.put'];
  };
}

export interface operations {
  'library.specs.list_': {
    responses: {
      /**
       * All the available specs
       */
      '200': {
        'application/json': components['schemas']['SpecInfo'][];
      };
      /**
       * Unauthorized
       */
      '401': {
        'text/plain': string;
      };
    };
  };
  'library.specs.get': {
    parameters: {
      path: {
        spec_id: components['parameters']['SpecId'];
      };
    };
    responses: {
      /**
       * The requested spec
       */
      '200': {
        'text/plain': components['schemas']['SpecValue'];
      };
      /**
       * Unauthorized
       */
      '401': {
        'text/plain': string;
      };
      /**
       * Spec was not found
       */
      '404': {
        'text/plain': string;
      };
    };
  };
  'library.specs.put': {
    parameters: {
      path: {
        spec_id: components['parameters']['SpecId'];
      };
      header: {
        /**
         * The language of the spec
         */
        'X-LANGUAGE': 'JSON' | 'YAML';
      };
    };
    requestBody: {
      'text/plain': components['schemas']['SpecValue'];
    };
    responses: {
      /**
       * The spec has been stored
       */
      '204': never;
      /**
       * The spec is not valid
       */
      '400': {
        'text/plain': string;
      };
      /**
       * Unauthorized
       */
      '401': {
        'text/plain': string;
      };
      /**
       * Payment required
       */
      '402': {
        'text/plain': string;
      };
      /**
       * Something went wrong whilst saving the spec
       */
      '500': {
        'text/plain': string;
      };
    };
  };
  'library.specs.delete': {
    parameters: {
      path: {
        spec_id: components['parameters']['SpecId'];
      };
    };
    responses: {
      /**
       * The spec has been deleted
       */
      '204': never;
      /**
       * Unauthorized
       */
      '401': {
        'text/plain': string;
      };
    };
  };
  'library.specs.versions.list_': {
    parameters: {
      path: {
        spec_id: components['parameters']['SpecId'];
      };
    };
    responses: {
      /**
       * All the available versions for a spec
       */
      '200': {
        'application/json': components['schemas']['SpecInfo'][];
      };
      /**
       * Unauthorized
       */
      '401': {
        'text/plain': string;
      };
      /**
       * Spec was not found
       */
      '404': {
        'text/plain': string;
      };
    };
  };
  'library.specs.versions.get': {
    parameters: {
      path: {
        spec_id: components['parameters']['SpecId'];
        version: components['parameters']['SpecVersion'];
      };
    };
    responses: {
      /**
       * The requested spec
       */
      '200': {
        'text/plain': components['schemas']['SpecValue'];
      };
      /**
       * Unauthorized
       */
      '401': {
        'text/plain': string;
      };
      /**
       * Spec was not found
       */
      '404': {
        'text/plain': string;
      };
    };
  };
  'library.specs.versions.put': {
    parameters: {
      path: {
        spec_id: components['parameters']['SpecId'];
        version: components['parameters']['SpecVersion'];
      };
      header: {
        /**
         * The language of the spec
         */
        'X-LANGUAGE': 'JSON' | 'YAML';
      };
    };
    requestBody: {
      'text/plain': components['schemas']['SpecValue'];
    };
    responses: {
      /**
       * The spec has been stored
       */
      '204': never;
      /**
       * The spec is not valid or there is a version mismatch in the path and spec
       */
      '400': {
        'text/plain': string;
      };
      /**
       * Unauthorized
       */
      '401': {
        'text/plain': string;
      };
      /**
       * Payment required
       */
      '402': {
        'text/plain': string;
      };
      /**
       * Something went wrong whilst saving the spec
       */
      '500': {
        'text/plain': string;
      };
    };
  };
}

export interface components {
  parameters: {
    /**
     * The id of the spec
     */
    SpecId: components['schemas']['SpecId'];
    /**
     * The version of the spec
     */
    SpecVersion: components['schemas']['SpecVersion'];
  };
  schemas: {
    /**
     * The id of an OpenAPI specification
     */
    SpecId: string;
    /**
     * The value of an OpenAPI specification
     */
    SpecValue: string;
    /**
     * The version of an OpenAPI specification
     */
    SpecVersion: string;
    /**
     * The last time the OpenAPI specification was updated
     */
    SpecUpdatedAt: number;
    /**
     * The title of an OpenAPI specification
     */
    SpecTitle: string;
    /**
     * The description of an OpenAPI specification
     */
    SpecDescription: string;
    /**
     * The number of models in an OpenAPI specification
     */
    SpecModelCount: number;
    /**
     * Information about a an OpenAPI specification
     */
    SpecInfo: {
      spec_id: components['schemas']['SpecId'];
      version: components['schemas']['SpecVersion'];
      updated_at?: components['schemas']['SpecUpdatedAt'];
      title?: components['schemas']['SpecTitle'];
      description?: components['schemas']['SpecDescription'];
      model_count: components['schemas']['SpecModelCount'];
    };
  };
}