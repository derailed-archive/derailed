import React from 'react'
import ReactDOM from 'react-dom/client'
import 'virtual:uno.css'
import './index.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'


const Register = React.lazy(() => import("./components/Register"))
const Login = React.lazy(() => import("./components/Login"))


let router = createBrowserRouter([
  {
    path: "/register",
    element: <React.Suspense children={<Register />}></React.Suspense>
  },
  {
    path: "/login",
    element: <React.Suspense children={<Login />}></React.Suspense>
  }
])

ReactDOM.createRoot(document.getElementById('app-mount')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
