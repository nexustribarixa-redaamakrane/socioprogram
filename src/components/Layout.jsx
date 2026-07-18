export default function Layout({ children }) {
    return (
        <div className="min-h-screen bg-[#0d1117] text-gray-200 p-6">
            <header className="max-w-2xl mx-auto border-b border-gray-700 pb-4 mb-8">
                <h1 className="font-bold text-xl tracking-tighter">SOCIOPROGRAM</h1>
                <p className="text-xs text-gray-500 uppercase tracking-widest">Protocol Active: Chronological Registry</p>
            </header>
            <main>{children}</main>
        </div>
    );
}
