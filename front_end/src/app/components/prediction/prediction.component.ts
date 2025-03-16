import { Component } from '@angular/core';
import { PredictionService } from 'src/app/services/prediction.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-prediction',
  templateUrl: './prediction.component.html',
  styleUrls: ['./prediction.component.css']
})
export class PredictionComponent {

  predictionForm: FormGroup;
  predictionResult: any = null;
  errorMessage: string = '';

  countries: string[] = ['Canada', 'Finland', 'Italy', 'Kenya', 'Norway', 'Singapore'];
  stores: string[] = ['Discount Stickers', 'Stickers for Less', 'Premium Sticker Mart'];
  products: string[] = ['Holographic Goose', 'Kaggle', 'Kaggle Tiers', 'Kerneler', 'Kerneler Dark Mode'];

  constructor(private predictionService: PredictionService, private fb: FormBuilder) {
    this.predictionForm = this.fb.group({
      country: ['', Validators.required],
      store: ['', Validators.required],
      product: ['', Validators.required],
      date: ['', [Validators.required, Validators.pattern('^\\d{4}-\\d{2}-\\d{2}$')]],
      num_sold: [0, Validators.required]
    });
  }

  onSubmit() {
    if (this.predictionForm.valid) {
      const data = this.predictionForm.value;

      this.predictionService.getPredictions(data).subscribe(
        (response) => {
          this.predictionResult = response.predictions;
        },
        (error) => {
          this.errorMessage = 'Error occurred: ' + error.error;
        }
      );
    } else {
      this.errorMessage = 'Please fill out the form correctly.';
    }
  }
}