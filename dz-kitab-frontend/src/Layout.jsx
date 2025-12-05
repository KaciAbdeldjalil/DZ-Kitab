import Footer from "./components/footer";
import Header from "./components/header";
export default function Layout({ children }) {
    return (
        <div className="layout">
            <Header></Header>
            <main>{children}</main>
            <Footer></Footer>
        </div>
    );
}
