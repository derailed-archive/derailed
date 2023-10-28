import React from 'react'
import ReactDOM from 'react-dom/client'
import 'virtual:uno.css'
import './index.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'


const Register = React.lazy(() => import("./pages/Register"))
const Login = React.lazy(() => import("./pages/Login"))
const WsTest = React.lazy(() => import("./pages/WsTest"))


const router = createBrowserRouter([
  {
    path: "/register",
    element: <React.Suspense children={<Register />}></React.Suspense>
  },
  {
    path: "/login",
    element: <React.Suspense children={<Login />}></React.Suspense>
  },
  {
    path: "/",
    element: <React.Suspense children={<WsTest />}></React.Suspense>
  }
])

ReactDOM.createRoot(document.getElementById('app-mount')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
