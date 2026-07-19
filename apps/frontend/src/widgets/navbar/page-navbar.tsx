import { Link } from "@tanstack/react-router";

import { appRoutes } from "@/shared/constants/routes"
import { useChatPetOptions } from "@/features/chat-pet-options/model/chat-pet-options";

import './navbar.css'


export function Navbar() {
    const pets = useChatPetOptions();

    return (
        <nav className="navbar">
            <Link to={appRoutes.home} className="navbar-item" activeProps={{className: "navbar-item-active"}}>
                <svg className="navbar-icon" viewBox="0 0 24 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12.001 1.81919C14.8197 -0.690289 19.1756 -0.606978 21.8907 2.09153C24.6059 4.79004 24.6991 9.08921 22.1739 11.8932L11.9997 22L1.82562 11.8932C-0.699529 9.08921 -0.605139 4.78324 2.10879 2.09153C4.82579 -0.603229 9.17405 -0.694014 12.001 1.81919ZM20.192 3.77291C18.3931 1.98511 15.4888 1.91259 13.6041 3.59054L12.0021 5.01679L10.3991 3.59166C8.50901 1.91135 5.60996 1.98527 3.80581 3.77466C2.01816 5.54768 1.92841 8.38737 3.57585 10.2629L11.9997 18.631L20.4237 10.2629C22.0718 8.38666 21.9824 5.55237 20.192 3.77291Z" fill="currentColor"/>
                </svg>
                <span className="main-button">главная</span>
            </Link>

            <Link to={appRoutes.map} className="navbar-item" activeProps={{className: "navbar-item-active"}}>
                <svg className="navbar-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M18.9401 17.2693L24 22.3292L22.3292 24L17.2693 18.9401C15.4499 20.3957 13.1427 21.2664 10.6332 21.2664C4.76368 21.2664 0 16.5028 0 10.6332C0 4.76368 4.76368 0 10.6332 0C16.5028 0 21.2664 4.76368 21.2664 10.6332C21.2664 13.1427 20.3957 15.4499 18.9401 17.2693ZM16.5697 16.3926C18.0144 14.9038 18.9035 12.8728 18.9035 10.6332C18.9035 6.06389 15.2025 2.36294 10.6332 2.36294C6.06389 2.36294 2.36294 6.06389 2.36294 10.6332C2.36294 15.2025 6.06389 18.9035 10.6332 18.9035C12.8728 18.9035 14.9038 18.0144 16.3926 16.5697L16.5697 16.3926Z" fill="currentColor"/>
                </svg>
                <span className="search-button">карта</span>
            </Link>

            {pets.pets.length === 1 ?
                <Link
                    to={appRoutes.chatHistory}
                    params={{ petId: String(pets.pets[0].id) }}
                    className="navbar-chat-button"
                >
                    <svg className="chat-button-icon" viewBox="0 0 25 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5.38258 19.3333L0 23.5625V1.20833C0 0.540995 0.540995 0 1.20833 0H22.9583C23.6257 0 24.1667 0.540995 24.1667 1.20833V18.125C24.1667 18.7924 23.6257 19.3333 22.9583 19.3333H5.38258Z" fill="#FAFAFA"/>
                    </svg>
                </Link>
                :
                <Link
                    to={appRoutes.chatSelectPet}
                    className="navbar-chat-button"
                >
                    <svg className="chat-button-icon" viewBox="0 0 25 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5.38258 19.3333L0 23.5625V1.20833C0 0.540995 0.540995 0 1.20833 0H22.9583C23.6257 0 24.1667 0.540995 24.1667 1.20833V18.125C24.1667 18.7924 23.6257 19.3333 22.9583 19.3333H5.38258Z" fill="#FAFAFA"/>
                    </svg>
                </Link>
            }

            <Link to={appRoutes.calendar} className="navbar-item" activeProps={{className: "navbar-item-active"}}>
                <svg className="navbar-icon" viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8.75 0V2.5H16.25V0H18.75V2.5H23.75C24.4404 2.5 25 3.05965 25 3.75V23.75C25 24.4404 24.4404 25 23.75 25H1.25C0.55965 25 0 24.4404 0 23.75V3.75C0 3.05965 0.55965 2.5 1.25 2.5H6.25V0H8.75ZM22.5 12.5H2.5V22.5H22.5V12.5ZM6.25 5H2.5V10H22.5V5H18.75V7.5H16.25V5H8.75V7.5H6.25V5Z" fill="currentColor"/>
                </svg>
                <span className="main-button">календарь</span>
            </Link>

            <Link to={appRoutes.userProfile} className="navbar-item" activeProps={{className: "navbar-item-active"}}>
                <svg className="navbar-icon" viewBox="0 0 21 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 25H18.375V22.619C18.375 20.6465 16.6122 19.0476 14.4375 19.0476H6.5625C4.38788 19.0476 2.625 20.6465 2.625 22.619V25H0V22.619C0 19.3317 2.93814 16.6667 6.5625 16.6667H14.4375C18.0618 16.6667 21 19.3317 21 22.619V25ZM10.5 14.2857C6.15076 14.2857 2.625 11.0877 2.625 7.14286C2.625 3.19796 6.15076 0 10.5 0C14.8492 0 18.375 3.19796 18.375 7.14286C18.375 11.0877 14.8492 14.2857 10.5 14.2857ZM10.5 11.9048C13.3994 11.9048 15.75 9.77279 15.75 7.14286C15.75 4.51293 13.3994 2.38095 10.5 2.38095C7.6005 2.38095 5.25 4.51293 5.25 7.14286C5.25 9.77279 7.6005 11.9048 10.5 11.9048Z" fill="currentColor"/>
                </svg>
                <span className="main-button">профиль</span>
            </Link>
        </nav>
    )
}