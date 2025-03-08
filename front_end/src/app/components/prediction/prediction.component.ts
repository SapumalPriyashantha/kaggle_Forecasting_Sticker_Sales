import { Component } from '@angular/core';
import { PredictionService } from 'src/app/services/prediction.service';

@Component({
  selector: 'app-prediction',
  templateUrl: './prediction.component.html',
  styleUrls: ['./prediction.component.css']
})
export class PredictionComponent {

  // Define variables for user input
  country: string = '';
  store: string = '';
  product: string = '';
  date: string = '';
  predictionResult: any = null;
  errorMessage: string = '';

  constructor(private predictionService: PredictionService) { }

  // Method to handle form submission
  onSubmit() {
    const data = {
      country: [this.country],
      store: [this.store],
      product: [this.product],
      date: [this.date]
    };

    // Call the prediction service to get predictions from Flask API
    this.predictionService.getPredictions(data).subscribe(
      (response) => {
        this.predictionResult = response.predictions;
      },
      (error) => {
        this.errorMessage = 'Error occurred: ' + error.message;
      }
    );
  }
}