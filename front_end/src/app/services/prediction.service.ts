import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PredictionService {

  // URL of your Flask backend
  private apiUrl = 'http://127.0.0.1:5000/predict';

  constructor(private http: HttpClient) { }

  // Make POST request to Flask API to get predictions
  getPredictions(data: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, data);
  }
}