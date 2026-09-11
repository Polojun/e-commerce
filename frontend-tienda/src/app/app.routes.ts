import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { Auth } from './components/auth/auth';

export const routes: Routes = [
    {path: '', component: Home},
    {path: 'login', component: Auth},
    { path: '**', redirectTo: '' }
];
