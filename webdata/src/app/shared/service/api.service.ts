import { Injectable } from '@angular/core';
import { Headers, Http, Response, URLSearchParams } from '@angular/http';
// import { HttpClientModule, HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { Observable } from 'rxjs';
import * as $ from "jquery";

@Injectable()
export class ApiService {

  private apiUrl = "/apis/";
  private apiGetUrl = "/apisget/";
  private apiUrlPost = "/apipost/";
  private apiGetDownload = "/downloadfile";

  constructor(private http: Http) { }

  private _handle_error(error:any) {
		if(error.status == 401 || error.status == 302 || error.status == 10 || error.status == 403 ){
			window.localStorage.clear();
			window.sessionStorage.clear();
			if('_body' in error){
				var link = error._body;
				if(link.indexOf('http') !== -1){
					location.href = link;
				}
			}
			else{
				location.reload();
			}
		};
		let message:string = (error.message) ? error.message :  error.status ? `${error.status} - ${error.statusText}` : 'Server error';
		return Observable.throw(message);
	}
    private _read_response(res:Response): object {
		let response = res.json();
		if('Result' in response){
			return response.Result;
		}
		return response;
	}

	public make_api_call(url: string, params:object={}): Observable<any>{
		let headers = new Headers();
    	this.createAuthorizationHeader(headers);

    	return this.http.post(this.apiUrlPost+url, params, {headers: headers})
         .map(this._read_response)
         .catch(this._handle_error);
	  };
	
		public downloadFile(urlStr:string, name:string){
			if(name === 'not-available'){
						 alert("Something went wrong please try again");
						 return;
				 }
				 var params = $.param({
								 name : name
				 });

			 const url = urlStr + '/sendfresponse' + '?' + params;
						 if($('#download-frame')){
				 $('#download-frame').attr('src', ' ');
				 $('#download-frame').remove('iframe');
						 }
						 $('body').append('<iframe id="download-frame" style="width:0;height:0;" src="' + url + '"></iframe');
			 setTimeout(function(){
				 $('#download-frame').attr('src', ' ');
				 $('#download-frame').remove('iframe');
			 },10000);
		 }

  	public download(name:string){
     if(name === 'not-available'){
            alert("Something went wrong please try again");
            return;
        }
        var params = $.param({
                name : name
        }),
			url = environment.origin + environment.api  + 'sendfresponse' + '?' + params;
            if($('#download-frame')){
			  $('#download-frame').attr('src', ' ');
        $('#download-frame').remove('iframe');
            }
            $('body').append('<iframe id="download-frame" style="width:0;height:0;" src="' + url + '"></iframe');
      setTimeout(function(){
        $('#download-frame').attr('src', ' ');
        $('#download-frame').remove('iframe');
      },10000);
  	}

	////////////////////////////////////

	createAuthorizationHeader(headers: Headers) {
		var token = this.getToken();
		if(token){
			headers.append('token', token);
		}
		else{
			headers.append('token', 'sometoken');
		}
  }

  getemptyapi(val,context) {
    return this.http.get(this.apiGetUrl,{params:{'input':val,context:context}})
    .map((res: Response) => res.json());
  }

  getapi(url) {
	let headers = new Headers();
    this.createAuthorizationHeader(headers);

    return this.http.get(this.apiUrl+url,{headers: headers})
    .map((res: Response) => res.json());
  }

  postapi(url,params){
	let headers = new Headers();
    this.createAuthorizationHeader(headers);
    return this.http.post(this.apiUrlPost+url,params,{headers: headers})
    .map((res: Response) => res.json());
	}
 
	applyDownload(apiKey,uuid){
		var url = environment.origin + environment.api + apiKey + '?uuid='+uuid+'&fname=Export';
		if($("#download-frame").length == 0) {
			$('body').append('<iframe id="download-frame" style="width:0;height:0;visibility:hidden;display:none;" src="' + url + '"></iframe');
		}else{
				$('#download-frame').attr('src', ' ');
				$('#download-frame').remove('iframe');
				$('body').append('<iframe id="download-frame" style="width:0;height:0;visibility:hidden;display:none;" src="' + url + '"></iframe');
		}
		return true;
	}
	
	getToken(){
    return sessionStorage.getItem('ct_token');
  }
}