import { Injector } from '@angular/core';
import { TestScheduler } from 'rxjs/testing';

import { MockStore, provideMockStore } from '@ngrx/store/testing';

import { AppState } from '../app.state';
import {
  initialState as initialPackageState,
  SpecsState,
  CredentialsState,
  Credentials,
} from './package.reducer';
import { PackageService } from './package.service';
import * as PackageActions from './package.actions';

const CREDENTIALS: Credentials = {
  // eslint-disable-next-line @typescript-eslint/naming-convention
  public_key: 'public key 1',
  // eslint-disable-next-line @typescript-eslint/naming-convention
  secret_key: 'secret key 1',
};

describe('PackageService', () => {
  let service: PackageService;
  let store: MockStore<AppState>;
  let testScheduler: TestScheduler;

  const initialState = { package: initialPackageState };

  beforeEach(() => {
    const injector = Injector.create({
      providers: provideMockStore({ initialState }),
    });
    store = injector.get(MockStore);
    service = new PackageService(store);

    testScheduler = new TestScheduler((actual, expected) => {
      expect(actual).toEqual(expected);
    });
  });

  describe('specs$', () => {
    it('should pick the correct state', () => {
      testScheduler.run((helpers) => {
        // GIVEN store with initial state and then a different state
        const specsState: SpecsState = {
          specInfos: [],
          loading: true,
          success: null,
        };
        helpers
          .cold('-b', {
            b: {
              ...initialState,
              package: { ...initialState.package, specs: specsState },
            },
          })
          .subscribe((newState) => store.setState(newState));

        // WHEN

        // THEN the specs state is returned
        helpers
          .expectObservable(service.specs$)
          .toBe('ab', { a: initialPackageState.specs, b: specsState });
      });
    });
  });

  describe('credentials$', () => {
    it('should pick the correct state', () => {
      testScheduler.run((helpers) => {
        // GIVEN store with initial state and then a different state
        const credentialsState: CredentialsState = {
          value: CREDENTIALS,
          loading: true,
          success: null,
        };
        helpers
          .cold('-b', {
            b: {
              ...initialState,
              package: {
                ...initialState.package,
                credentials: credentialsState,
              },
            },
          })
          .subscribe((newState) => store.setState(newState));

        // WHEN

        // THEN the credentials state is returned
        helpers.expectObservable(service.credentials$).toBe('ab', {
          a: initialPackageState.credentials,
          b: credentialsState,
        });
      });
    });
  });

  describe('specsComponentOnInit', () => {
    it('should dispatch specs component on init action', () => {
      testScheduler.run((helpers) => {
        // GIVEN a trigger for specsComponentOnInit
        helpers.cold('-b').subscribe(() => service.specsComponentOnInit());

        // WHEN

        // THEN store emits the expected actions
        helpers.expectObservable(store.scannedActions$).toBe('ab', {
          a: { type: '@ngrx/store/init' },
          b: PackageActions.specsComponentOnInit(),
        });
      });
    });
  });

  describe('specsComponentRefresh', () => {
    it('should dispatch specs component refresh action', () => {
      testScheduler.run((helpers) => {
        // GIVEN a trigger for specsComponentRefresh
        helpers.cold('-b').subscribe(() => service.specsComponentRefresh());

        // WHEN

        // THEN store emits the expected actions
        helpers.expectObservable(store.scannedActions$).toBe('ab', {
          a: { type: '@ngrx/store/init' },
          b: PackageActions.specsComponentRefresh(),
        });
      });
    });
  });

  describe('specsComponentDeleteSpec', () => {
    it('should dispatch specs component delete spec', () => {
      testScheduler.run((helpers) => {
        // GIVEN a trigger for specsComponentDeleteSpec
        const specName = 'spec 1';
        helpers
          .cold('-b')
          .subscribe(() => service.specsComponentDeleteSpec(specName));

        // WHEN

        // THEN store emits the expected actions
        helpers.expectObservable(store.scannedActions$).toBe('ab', {
          a: { type: '@ngrx/store/init' },
          b: PackageActions.specsComponentDeleteSpec({ specName }),
        });
      });
    });
  });
});
