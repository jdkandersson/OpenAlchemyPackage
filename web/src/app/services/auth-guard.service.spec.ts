import { OAuthService } from 'angular-oauth2-oidc';

import { AuthGuard } from './auth-guard.service';

import { environment } from '../../environments/environment';

const MOCK_ACTIVATED_ROUTE_SNAPSHOT = jasmine.createSpyObj(
  'ActivatedRouteSnapshot',
  ['params']
);

describe('AuthGuard', () => {
  let service: AuthGuard;
  let oAuthServiceSpy: jasmine.SpyObj<OAuthService>;

  beforeEach(() => {
    oAuthServiceSpy = jasmine.createSpyObj('OAuthService', [
      'hasValidIdToken',
      'hasValidAccessToken',
      'initLoginFlow',
    ]);
    service = new AuthGuard(oAuthServiceSpy);
  });

  afterEach(() => {
    sessionStorage.clear();
  });

  describe('canActivate', () => {
    it('it should return true if the token is present', () => {
      // GIVEN OAuthService that returns true for hasValidAccessToken
      oAuthServiceSpy.hasValidAccessToken.and.returnValue(true);

      // WHEN canActivate is called
      const result = service.canActivate(MOCK_ACTIVATED_ROUTE_SNAPSHOT, {
        url: 'url 1',
        root: MOCK_ACTIVATED_ROUTE_SNAPSHOT,
      });

      // THEN true is returned
      expect(result).toBeTrue();
      // AND initLoginFlow is not called
      expect(oAuthServiceSpy.initLoginFlow).not.toHaveBeenCalled();
      // AND noting was written into sessionStorage
      expect(
        sessionStorage.getItem(environment.signInCompleteReturnPathKey)
      ).toBeNull();
    });

    [
      {
        description: 'no access token',
        hasValidAccessToken: false,
      },
    ].forEach(({ description, hasValidAccessToken }) => {
      describe(description, () => {
        it('should init the login flow and store the current path', () => {
          // GIVEN OAuthService that returns values and hasValidAccessToken
          oAuthServiceSpy.hasValidAccessToken.and.returnValue(
            hasValidAccessToken
          );
          const url = 'url 1';

          // WHEN canActivate is called
          const result = service.canActivate(MOCK_ACTIVATED_ROUTE_SNAPSHOT, {
            url,
            root: MOCK_ACTIVATED_ROUTE_SNAPSHOT,
          });

          // THEN true is returned
          expect(result).toBeFalse();
          // AND initLoginFlow is not called
          expect(oAuthServiceSpy.initLoginFlow).toHaveBeenCalled();
          // AND noting was written into sessionStorage
          expect(
            sessionStorage.getItem(environment.signInCompleteReturnPathKey)
          ).toEqual(url);
        });
      });
    });
  });
});
