/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { PredictionService } from './prediction.service';

describe('Service: Prediction', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [PredictionService]
    });
  });

  it('should ...', inject([PredictionService], (service: PredictionService) => {
    expect(service).toBeTruthy();
  }));
});
