import { Link } from "@tanstack/react-router";
import { appRoutes } from "@/shared/constants/routes";

import './home-page.css';

import aichatIcon from './assets/aichatIcon.svg';

import arrowIcon from './assets/arrowIcon.svg';

import homeNavbar from './assets/heartNavbar.svg';
import profileNavbar from './assets/mainNavbar.svg';
import searchNavbar from './assets/searchNavbar.svg';
import calendarNavbar from './assets/calendarNavbar.svg';

import mapIcon from './assets/mapIcon.svg';
import clinicIcon from './assets/clinicIcon.svg';
import documentsIcon from './assets/documentsIcon.svg';
import aiIcon from './assets/aiIcon.svg';

import notificationHeader from './assets/notificationHeader.svg';
import petcareLogo from './assets/petcarelogo.svg';
import user_photo from './assets/user_photo.png'

import photo1 from './assets/photo1.png';
import photo2 from './assets/photo2.png';

import calendarPet from './assets/calendarPet.svg';
import weightPet from './assets/weightPet.svg';

type Pet = {
    id: number;
    name: string;
    breed: string;
    age: string;
    weight: string;
    image: string;
}

type Service = {
    id: number;
    icon: string;
    title: string;
    description: string;
}

const pets: Pet[] = [
    {
        id: 1,
        name: 'Лола',
        breed: 'ЙОРКШИРСКИЙ ТЕРЬЕР',
        age: '3 года',
        weight: '5 кг',
        image: photo1
    },
    {
        id: 2,
        name: 'Чакки',
        breed: 'САМОЕД',
        age: '5 лет',
        weight: '10 кг',
        image: photo2
    },
];

const services: Service[] = [
    {
        id: 1,
        icon: clinicIcon,
        title: "Клиники",
        description: "Советы и помощь"
    },
    {
        id: 2,
        icon: aiIcon,
        title: "ИИ-помощник",
        description: "Советы и помощь"
    },
    {
        id: 3,
        icon: mapIcon,
        title: "Места",
        description: "Советы и помощь"
    },
    {
        id: 4,
        icon: documentsIcon,
        title: "Документы",
        description: "Советы и помощь"
    },
];

export const HomePage = () => {
    return (
        <div className="home-page page-transition">
            <header className="home-header">
                <button type="button" className="brand">
                    <img src={petcareLogo} alt="PetCare" className="logo"/>
                    <div className="title">PetCare</div>
                </button>
                
                <div className="header-content">
                    <button type="button" className="notifications-button">
                        <img src={notificationHeader} alt="Уведомления" className="notifications-button-img"/>
                    </button>
                    
                    <button type="button" className="profile-button">
                        <img src={user_photo} alt="Профиль"/>
                    </button>
                </div>
            </header>

            <section className="home-section">
                <h2 className="section-title">Ближайшие события:</h2>
                
                <button type="button" className="event-card">
                    <div className="event-date">
                        <span className="event-month">апр</span>
                        <span className="event-day">08</span>
                    </div>
                    
                    <div className="event-info">
                        <p className="event-title">Ежегодная вакцинация</p>
                        <p className="event-subtitle">{pets[0].name} • Ежегодная вакцинация</p>
                    </div>
                </button>
            </section>

            <section className="pets-section">
                <div className="section-row">
                    <h2 className="section-title">Мои питомцы</h2>
                    <button type="button" className="add-pet-button">+ Добавить</button>
                </div>

                <div className="pets-list">
                    {pets.map((pet) => (
                        <button type="button" className="pet-card" key={pet.id}>
                            <div className="pet-main">
                                <img src={pet.image} alt={pet.name} className="pet-image"/>
                                
                                <div className="pet-info">
                                    <p className='pet-name'>{pet.name}</p>
                                    <p className='pet-breed'>{pet.breed}</p>

                                    <div className="pet-meta">
                                        <span className="pet-meta-item">
                                            <img src={calendarPet} alt="" className="pet-meta-icon"/>
                                            {pet.age}
                                        </span>

                                        <span className="pet-meta-item">
                                            <img src={weightPet} alt="" className="pet-meta-icon"/>
                                            {pet.weight}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        
                        <img src={arrowIcon} alt="" className="arrow-icon"/>
                        
                        </button>
                    ))} 
                </div>
            </section>

            <section className="service-section">
                <h2 className="section-title">Сервисы</h2>

                <div className="service-list">
                    {services.map((service) => (
                        <button type="button" className="service-card" key={service.id}>
                            <img src={service.icon} alt={service.title} className="service-icon"/>
                            <div className="service-text">
                                <p className="service-title">{service.title}</p>
                                <p className="service-description">{service.description}</p>
                            </div>
                        </button>
                    ))}
                </div>
            </section>

            <nav className="bottom-navbar">
                <button type="button" className="navbar-item">
                    <img src={homeNavbar} alt="" className="navbar-icon"/>
                    <span className="main-button">главная</span>
                </button>

                <button type="button" className="navbar-item">
                    <img src={searchNavbar} alt="" className="navbar-icon"/>
                    <span className="search-button">поиск</span>
                </button>

                <button type="button" className="navbar-item">
                    <img src={aichatIcon} alt="" className="navbar-icon"/>
                </button>

                <button type="button" className="navbar-item">
                    <img src={calendarNavbar} alt="" className="navbar-icon"/>
                    <span className="main-button">календарь</span>
                </button>

                <Link to={appRoutes.userProfile} className="navbar-item">
                    <img src={profileNavbar} alt="" className="navbar-icon"/>
                    <span className="main-button">профиль</span>
                </Link>
            </nav>
        </div>
    );
};