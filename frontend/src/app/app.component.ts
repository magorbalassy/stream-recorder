import { Component, OnInit, ViewChild } from '@angular/core';
import { Job } from './models';
import { BackendService } from './backend.service';
import { FormControl, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTable } from '@angular/material/table';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{

  title = 'stream-recorder';
  jobs : Job[] = [];
  displayedColumns: string[] = ['id', 'filename', 'start_date', 'length', 'url', 'actions'];

  // Form values
  time = "17:00";
  length = 30;
  filename = "Video stream ABC <datetime>";
  url = "http://tv.com:80/video/stream";
  time_validator: FormControl = new FormControl();
  length_validator: FormControl = new FormControl();
  datepicker: FormControl = new FormControl();

  @ViewChild(MatTable) jobstable!: MatTable<any>;

  constructor(private backendService: BackendService, 
              private snackBar: MatSnackBar) {
    this.getJobs();
  }

  getJobs () {
    this.backendService.getJobs()
      .subscribe( (data) => {
        this.jobs = data;
      });
  }

  delete(id:number) {
    console.log('id,',id);
    let idx = this.jobs.findIndex((job:Job) => job.id == id)
    this.backendService.deleteJob(this.jobs[idx])
      .subscribe( res => {
        if (res == 0 ) {
          this.openSnackBar('Error - couldn\'t delete job','Close','red-snackbar');
        } else {
          this.openSnackBar('Job with id ' + String(res) + ' deleted.','Close','red-snackbar');
          let idx = this.jobs.findIndex((job:Job) => job.id == res);
          this.jobs.splice(idx, 1);
          this.refresh();
        }
      });
  }
  
  edit(id: number) {

  }

  submit() {
    console.log('submit', this.datepicker, this.time_validator.value, this.time_validator);
    if ((!this.time_validator.valid) || !(this.length_validator.valid)) {
      this.openSnackBar('Invalid values in form, please correct.','Close','red-snackbar');
    } else {
      let hour = this.time_validator.value.slice(0, 2) as number;
      let minutes = this.time_validator.value.slice(3, 5) as number;
      let start_date = new Date(this.datepicker.value);
      let now = new Date();
      console.log('dates: ', start_date.valueOf() - now.valueOf() );
      console.log(':', start_date);
      console.log(':', now);
      console.log(':', start_date);
      console.log(':', now);
      start_date.setHours(hour);
      start_date.setMinutes(minutes);
      start_date.setSeconds(0);
      start_date.setMilliseconds(0);
      if ( start_date.valueOf() < now.valueOf() ) {
        this.openSnackBar('Start time is in the past, can\'t schedule.','Close','red-snackbar');
        return;
      }
      console.log(start_date);
      let job = { filename : this.filename,
                length : this.length_validator.value,
                url : this.url,
                status : "new",
                start_date : start_date.valueOf(),
                created_on : "",
                id: 0
                } as Job;
      console.log('posting : ', job)
      this.backendService.postJob(job)
              .subscribe( data  => {
                if (data == 0) {
                  this.openSnackBar('Job exists already','Close','red-snackbar');
                } else {
                  job.id = data;
                  //job.start_date = new Date(job.start_date);
                  this.jobs.push(job);
                  this.openSnackBar('Job created with id ' + String(data),'Close','red-snackbar');
                  this.refresh();
                }
              });
    }
  }

  refresh() { this.jobstable.renderRows();  }

  openSnackBar(message: string, action: string, className: string) {
    this.snackBar.open(message, action, {
     duration: 10000,
     verticalPosition: 'top',
     horizontalPosition: 'end',
     panelClass: [className],
   });
}

  ngOnInit(): void {
    this.time_validator = new FormControl(this.time, [Validators.required, Validators.pattern(/^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$/)]);
    this.length_validator = new FormControl(this.length, [Validators.required, Validators.pattern("^[0-9]*$")]);
    this.datepicker.setValue(new Date());
  }

}
