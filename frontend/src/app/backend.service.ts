import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Job } from './models'

@Injectable({
  providedIn: 'root'
})
export class BackendService {

  private url = '/api/';

  constructor(private http: HttpClient) { }

  getJobs(): Observable<Job[]> {
    return this.http.get<Job[]>(this.url);  
  }

  postJob(job: Job): Observable<number> {
    console.log('post service');
    const headers = { 'content-type': 'application/json'};
    return this.http.post<number>(this.url, job, {headers});
  }

  deleteJob(job: Job): Observable<number> {
    console.log('delete service');
    const headers = { 'content-type': 'application/json'};
    return this.http.delete<number>(this.url + '/', {headers: headers, body:job});
  }
}
