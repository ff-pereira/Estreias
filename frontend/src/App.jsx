import { BrowserRouter, Routes, Route } from 'react-router-dom';

import HomePage from "./pages/HomePage";
import Header from './components/Header';
import Body from "./components/Body.jsx";
import FilmPage from "./pages/FilmPage.jsx";
import FilmsPage from "./pages/FilmsPage.jsx";
import StatsPage from "./pages/StatsPage.jsx";
import ErrorPage from "./pages/ErrorPage.jsx";
import PersonPage from "./pages/PersonPage.jsx";
import CinemaPage from "./pages/CinemaPage.jsx";
import ApiProvider from "./contexts/ApiProvider";
import PersonsPage from "./pages/PersonsPage.jsx";
import CinemasPage from "./pages/CinemasPage.jsx";
import FlashProvider from "./contexts/FlashProvider";


/**
 * @author ffpereira
 */
function AppContent() {
    return (
        <>
            <Header />
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/stats" element={<StatsPage type="stats"/>} />
                <Route path="/films" element={<FilmsPage />} />
                <Route path="/persons" element={<PersonsPage />} />
                <Route path="/cinemas" element={<CinemasPage />} />
                <Route path="/film/:film_id" element={<FilmPage />} />
                <Route path="/person/:person_id" element={<PersonPage />} />
                <Route path="/cinema/:cinema_id" element={<CinemaPage />} />
                <Route path="/genre/:detail_id" element={<StatsPage type="genre"/>} />
                <Route path="/country/:detail_id" element={<StatsPage type="country"/>} />
                <Route path="/language/:detail_id" element={<StatsPage type="language"/>} />
                <Route path="/release_year/:detail_id" element={<StatsPage type="release_year"/>} />
                <Route path="/pt_release_year/:detail_id" element={<StatsPage type="pt_release_year"/>} />
                <Route path="/month/:detail_id" element={<StatsPage type="month"/>} />
                <Route path="/runtime/:detail_id" element={<StatsPage type="runtime"/>} />
                <Route path="/distributor/:detail_id" element={<StatsPage type="distributor"/>} />
                <Route path="/content_rating/:detail_id" element={<StatsPage type="content_rating"/>} />
                <Route path="*" element={<Body><ErrorPage code="404"/></Body>} />
            </Routes>
        </>
    );
}

export default function App() {
    return (
        <div>
            <BrowserRouter>
                <FlashProvider>
                    <ApiProvider>
                        <AppContent />
                    </ApiProvider>
                </FlashProvider>
            </BrowserRouter>
        </div>
    );
}
