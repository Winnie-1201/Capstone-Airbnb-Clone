import React, { useState, useEffect } from "react";
import { BrowserRouter, Route, Switch } from "react-router-dom";
import { useDispatch } from "react-redux";
import { authenticate } from "./store/session";
import Test from "./components/auth/Test";
import { getAllSpotThunk } from "./store/spots";
import Homepage from "./components/Homepage";
import LoginForm from "./components/LoginSignup/LoginForm";
import SpotDetails from "./components/Spots/SpotDetails";

function App() {
  const [loaded, setLoaded] = useState(false);
  const dispatch = useDispatch();

  useEffect(() => {
    (async () => {
      await dispatch(authenticate());
      await dispatch(getAllSpotThunk());
      setLoaded(true);
    })();
  }, [dispatch]);

  if (!loaded) {
    return null;
  }

  return (
    <BrowserRouter>
      <Switch>
        <Route path="/test" exact={true}>
          <LoginForm />
        </Route>
        <Route path="/spots/:spotId" exact={true}>
          <SpotDetails />
        </Route>
        <Route path="/" exact={true}>
          <Homepage />
        </Route>
      </Switch>
    </BrowserRouter>
  );
}

export default App;
