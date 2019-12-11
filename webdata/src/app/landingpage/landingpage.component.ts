import { Component, OnInit, ViewChild } from '@angular/core';
import { ApiService } from '../shared/service/api.service';
import { Directive, HostListener } from '@angular/core';

@Component({
  selector: 'app-landingpage',
  templateUrl: './landingpage.component.html',
  styleUrls: ['./landingpage.component.scss']
})

// @HostListener('scroll', ['$event.target'])

export class LandingpageComponent implements OnInit {

	@ViewChild("container", { static: false }) container:any;

	public category:Array<Object> = [];
	public selected_category: Object = {};
	public if_category:boolean = false;
	public refresh_search:boolean = false;
	public search_text:string = null;
	public limit:number = 25;
	public pageTo:number = 10;
	public pageFrom: number = 0;
	public all_records:Array<Object> = [];
	public book_records:Array<Object> = [];
	public imageToShow:any;
	public colSize:number = 4;
	public innerWidth: number = 0;
	public searchText:string = null;

	constructor(private api$: ApiService) { }

	public get_summary(): void {
		let params = {
			"topic": this.selected_category["name"],
			'pageTo': this.pageTo, 
			'pageFrom': this.pageFrom,
			"search": this.searchText
		}

		console.log(params);

		this.refresh_search = false;
		this.api$.make_api_call("getsummarydata", params).subscribe(d => {
			console.log(d);
			d.forEach(ele => {
				this.all_records.push(ele);
			});
			this.book_records = this.all_records;
			// location.reload();
			this.pageFrom = this.pageFrom + this.limit;
			this.pageTo = this.pageTo + this.limit;
			this.refresh_search = true;

		});
	}

	private setColSize() {
	    this.colSize = 4;
	    if(this.innerWidth > 1600){
			this.colSize = 9;
		}else if(this.innerWidth < 1400 && this.innerWidth >= 1135){
			this.colSize = 7;
		}
		else if(this.innerWidth < 1135 && this.innerWidth >= 720){
			this.colSize = 5;
		}
		else if(this.innerWidth < 720){
			this.colSize = 4;
		}
  }

	public onCategoryClick(cat){
		this.selected_category = cat;
		this.search_text = null;
		this.if_category = true;
		this.resetPage();
		this.get_summary();
	}

	public goBack() {
		this.if_category = false;
		this.selected_category = {};
	}

	public onSearchTextChange(){
		this.resetPage();
		this.get_summary();
	}

	public clearSearch(){
		this.searchText = null;
		this.resetPage();
		this.get_summary();
	}

	public resetPage(){
		this.pageTo = this.limit;
		this.pageFrom = 0;
		this.all_records = [];
		this.book_records = [];
	}

	public onBookClick(book:Object){
		let formats = book["format"];

		let url = null;
		formats.forEach(ele =>{
			if(ele["mime_type"] === "text/html; charset=utf-8" || ele["mime_type"] === "text/plain; charset=iso-8859-1"){
				url = ele["url"];
			}
		});

		if(url !== null){
			window.open(url);	
		}
		else{
			alert("No viewable version available");
		}
		
	}

	public onScroll(){
		if(( this.container.nativeElement.offsetHeight + this.container.nativeElement.scrollTop) >=  this.container.nativeElement.scrollHeight) {
			this.get_summary();
		}
	}

  	ngOnInit() {
  		this.resetPage();

  		this.if_category = false;
  		this.selected_category = {};
  		// this.selected_category = {
  		// 	"display": "FICTION",
  		// 	"label":"Fiction",
  		// 	"name": "Fiction",
  		// 	"icon": "fa fa-flask"
  		// };

  		// this.get_summary();
  		// this.getImageFromService();

  		this.category = [{
  			"display": "FICTION",
  			"label":"Fiction",
  			"name": "Fiction",
  			"icon": "fa fa-flask"
  		},{
  			"display": "PHILOSOPHY",
  			"label": "Philosophy",
  			"name":"Philosophy",
  			"icon": "fas fa-yin-yang"
  		},{
  			"display":"DRAMA",
  			"label":"Drama",
  			"name":"Drama",
  			"icon": "fas fa-theater-masks"
  		},{
  			"display":"HISTORY",
  			"label":"History",
  			"name": "History",
  			"icon": "fas fa-torah"
  		},{
  			"display":"HUMOR",
  			"label":"Humor",
  			"name":"Humor",
  			"icon":"fas fa-laugh-beam"
  		},{
  			"display":"ADVENTURE",
  			"label":"Adventure",
  			"name":"Adventure",
  			"icon":"fas fa-compass"
  		},{
  			"display":"POLITICS",
  			"label":"Politics",
  			"name":"Politics",
  			"icon":"fas fa-vote-yea"
  		}]
  	}

  	ngOnDestroy() {
        // window.removeEventListener('scroll', this.scrollEvent, true);
    }


}
