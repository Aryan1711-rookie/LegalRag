import {
  BrowserRouter,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";

import Research from "./pages/Research";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoutes";
import Settings from "./pages/Settings";
import Documents from "./pages/Documents";
import Home from "./pages/Home";
import PageTransition from "./components/PageTransition";
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<PageTransition><Login /></PageTransition>} />
          <Route path="/register" element={<PageTransition><Register /></PageTransition>} />
          <Route path="/" element={<PageTransition><Home /></PageTransition>} />
          <Route element={<ProtectedRoute />}>
            {/* <Route
              path="/"
              element={<Navigate to="/research" replace />}
            /> */}

            <Route
              path="/research"
              element={<PageTransition><Research /></PageTransition>}
            />

            <Route
              path="/research/:documentSlug"
              element={<PageTransition><Research /></PageTransition>}
            />

            <Route
              path="/research/:documentSlug/:chatId"
              element={<PageTransition><Research /></PageTransition>}
            />

            <Route
              path="/settings"
              element={<PageTransition><Settings /></PageTransition>}
              
            />
            <Route path="/documents" element={<PageTransition><Documents /></PageTransition>} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;