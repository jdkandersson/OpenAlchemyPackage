import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { By } from '@angular/platform-browser';

import { TestScheduler } from 'rxjs/testing';
import { map } from 'rxjs/operators';

import { SpecsComponent } from './specs.component';
import { SpecInfo } from '../../services/package/types';
import { PackageService } from '../../services/package/package.service';

const SPEC_INFO: SpecInfo = {
  spec_id: 'spec id 1',
  version: 'version 1',
  model_count: 1,
};

@Component({ selector: 'app-specs-table', template: '' })
class AppSpecsTableStubComponent {
  @Input() specInfos: SpecInfo[] = [];
}

@Component({ selector: 'app-specs-refresh-button', template: '' })
class AppSpecsRefreshButtonStubComponent {
  @Input() loading: boolean = true;
  @Output() refreshEvent = new EventEmitter<void>();
}

describe('SpecsComponent', () => {
  let component: SpecsComponent;
  let fixture: ComponentFixture<SpecsComponent>;
  let packageServiceSpy: jasmine.SpyObj<PackageService>;
  let testScheduler: TestScheduler;

  beforeEach(() => {
    packageServiceSpy = jasmine.createSpyObj('PackageService', [
      'specs$',
      'specsComponentOnInit',
    ]);

    TestBed.configureTestingModule({
      declarations: [
        SpecsComponent,
        AppSpecsTableStubComponent,
        AppSpecsRefreshButtonStubComponent,
      ],
      providers: [{ provide: PackageService, useValue: packageServiceSpy }],
    });

    fixture = TestBed.createComponent(SpecsComponent);
    component = fixture.componentInstance;

    testScheduler = new TestScheduler((actual, expected) => {
      expect(actual).toEqual(expected);
    });
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('ngOnInit', () => {
    it('should call specsComponentOnInit on PackageService on init', () => {
      // GIVEN that specsComponentOnInit has not been called
      expect(packageServiceSpy.specsComponentOnInit).toHaveBeenCalledTimes(0);

      // WHEN onInit is triggered
      component.ngOnInit();

      // GIVEN that specsComponentOnInit has been called
      expect(packageServiceSpy.specsComponentOnInit).toHaveBeenCalledOnceWith();
    });
  });

  describe('app-specs-table', () => {
    it('should pass the specs to app-specs-table', () => {
      testScheduler.run((helpers) => {
        // GIVEN specs$ that initially is empty and then has specs
        packageServiceSpy.specs$ = helpers.cold('ab', {
          a: { specInfos: [], loading: false, success: null },
          b: { specInfos: [SPEC_INFO], loading: false, success: null },
        });

        // WHEN changes are detected
        fixture.detectChanges();

        // THEN the specInfos are passed to app-specs-table
        const componentSpecInfos$ = helpers.cold('ab').pipe(
          map(() => {
            fixture.detectChanges();
            const specsTableDebugElement = fixture.debugElement.query(
              By.directive(AppSpecsTableStubComponent)
            );
            const specsTableComponent = specsTableDebugElement.injector.get(
              AppSpecsTableStubComponent
            );
            return specsTableComponent.specInfos;
          })
        );
        helpers
          .expectObservable(componentSpecInfos$)
          .toBe('ab', { a: [], b: [SPEC_INFO] });
      });
    });
  });

  describe('app-specs-refresh-button', () => {
    it('should pass loading to app-specs-refresh-button', () => {
      testScheduler.run((helpers) => {
        // GIVEN specs$ that initially has loading false, then true
        packageServiceSpy.specs$ = helpers.cold('ab', {
          a: { specInfos: [], loading: false, success: null },
          b: { specInfos: [], loading: true, success: null },
        });

        // WHEN changes are detected
        fixture.detectChanges();

        // THEN the loading is passed to app-specs-refresh-button
        const componentLoading$ = helpers.cold('ab').pipe(
          map(() => {
            fixture.detectChanges();
            const refreshButtonDebugElement = fixture.debugElement.query(
              By.directive(AppSpecsRefreshButtonStubComponent)
            );
            const refreshButtonComponent = refreshButtonDebugElement.injector.get(
              AppSpecsRefreshButtonStubComponent
            );
            return refreshButtonComponent.loading;
          })
        );
        helpers
          .expectObservable(componentLoading$)
          .toBe('ab', { a: false, b: true });
      });
    });
  });
});
