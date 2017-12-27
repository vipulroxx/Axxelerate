import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, Params } from '@angular/router';
import { NotFoundComponent } from '../not-found/not-found.component';
import { QueryService } from '../query.service';
import { ResultPage } from '../result-page';
import { Result } from '../result';

@Component({
  selector: 'app-result-page',
  templateUrl: './result-page.component.html',
  styleUrls: ['./result-page.component.css']
})
export class ResultPageComponent implements OnInit {

  private query : string;
  private data : ResultPage;

  private prevFrom: string;
  private nextFrom : string;
  private fromId : string;

  private hasPrev : boolean = false;
  private hasNext : boolean = false;

  private results : Result[] = [];
  private badQuery: boolean = false;
  
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private queryService : QueryService
  ) { }

  ngOnInit() {
    this.route.queryParams.subscribe(
      value => {
        var query = value["q"];
        var fromId = value["f"];
        if ( query === undefined ) {
          this.badQuery = true;
        } else {
          this.query = query;
          this.fromId = fromId;
          this.queryService.submitQuery(query,fromId).subscribe(
            value => {
              this.results = value.results;
              this.hasPrev = (value.prevFrom !== undefined);
              this.hasNext = (value.nextFrom !== undefined);

              this.prevFrom = value.prevFrom;
              this.nextFrom = value.nextFrom;
            },
            error => {
              console.log("Failure in fetching data:");
            });
        }
      },
      error => console.log("error:" + error),
      () => console.log("finished")
    );
  }

  submitQuery(query : string) {
    this.router.navigate(["search"], {queryParams: {q: query}});
  }

}
