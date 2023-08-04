import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  createBrowserRouter,
  RouterProvider
} from 'react-router-dom';


const router = createBrowserRouter([
  {
    path: '/',
    element: <div />
  }
]);


ReactDOM.createRoot(document.getElementById('app')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
