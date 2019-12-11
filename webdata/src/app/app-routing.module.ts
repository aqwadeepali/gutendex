import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { LandingpageComponent } from './landingpage/landingpage.component';


const routes: Routes = [];

@NgModule({
  imports: [RouterModule.forRoot(routes),
  RouterModule.forRoot([
      {
        path: '',
        component: LandingpageComponent
      }
      
    ],{useHash:true})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
