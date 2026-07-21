export default function Layout({ children }) {
    return (
        <div className="app-shell">
            <header className="app-header">
                <h1 className="app-header__title">SOCIOPROGRAM</h1>
                <p className="app-header__subtitle">Protocol Active: Chronological Registry</p>
            </header>
            <main>{children}</main>
        </div>
    );
}
