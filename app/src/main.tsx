import React from 'react'
import ReactDOM from 'react-dom/client'
import 'virtual:uno.css'
import './index.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'


const Register = React.lazy(() => import("./components/Register"))


let router = createBrowserRouter([
  {
    path: "/register",
    element: <React.Suspense children={<Register />}></React.Suspense>
  }
])

ReactDOM.createRoot(document.getElementById('app-mount')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
