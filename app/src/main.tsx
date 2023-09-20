import React from 'react'
import ReactDOM from 'react-dom/client'
import 'virtual:uno.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

let router = createBrowserRouter([

])

ReactDOM.createRoot(document.getElementById('app-mount')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
