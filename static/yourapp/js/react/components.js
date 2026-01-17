/**
 * Safe Let Stays - React Components Library
 * ==========================================
 * Reusable React components for the entire application
 */

const { useState, useEffect, useRef, createContext, useContext } = React;

// ============================================================================
// CONTEXT
// ============================================================================

const SiteContext = createContext(window.SITE_DATA || {});

const useSiteData = () => useContext(SiteContext);

// ============================================================================
// ICONS
// ============================================================================

const Icons = {
    Phone: () => (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>
        </svg>
    ),
    Menu: () => (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
    ),
    Close: () => (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
    ),
    Location: () => (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
        </svg>
    ),
    Bed: () => (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M2 4v16"/><path d="M2 8h18a2 2 0 0 1 2 2v10"/><path d="M2 17h20"/>
            <path d="M6 8v9"/>
        </svg>
    ),
    Bath: () => (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 12h16a1 1 0 0 1 1 1v3a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4v-3a1 1 0 0 1 1-1z"/>
            <path d="M6 12V5a2 2 0 0 1 2-2h3v2.25"/>
            <circle cx="12" cy="5" r="1.25"/>
        </svg>
    ),
    Users: () => (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
    ),
    Star: ({ filled }) => (
        <svg width="16" height="16" viewBox="0 0 24 24" fill={filled ? "#FFD700" : "none"} stroke="#FFD700" strokeWidth="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
    ),
    Calendar: () => (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
    ),
    Check: () => (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="20 6 9 17 4 12"/>
        </svg>
    ),
    ChevronDown: () => (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M6 9l6 6 6-6"/>
        </svg>
    ),
    Share: () => (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
            <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
            <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
        </svg>
    ),
    Heart: ({ filled }) => (
        <svg width="18" height="18" viewBox="0 0 24 24" fill={filled ? "#e53935" : "none"} stroke={filled ? "#e53935" : "currentColor"} strokeWidth="2">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
    ),
    ArrowRight: () => (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="5" y1="12" x2="19" y2="12"/>
            <polyline points="12 5 19 12 12 19"/>
        </svg>
    ),
    Money: () => (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
        </svg>
    ),
    Verified: () => (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
    ),
    Flexible: () => (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
    ),
    Filter: () => (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
        </svg>
    ),
    Search: () => (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
    ),
    Loading: () => (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="animate-spin">
            <circle cx="12" cy="12" r="10" strokeOpacity="0.25"/>
            <path d="M12 2a10 10 0 0 1 10 10" strokeLinecap="round"/>
        </svg>
    )
};

// ============================================================================
// HEADER COMPONENT
// ============================================================================

const Header = ({ activePage }) => {
    const [menuOpen, setMenuOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const [searchDocked, setSearchDocked] = useState(false);
    const [searchSummary, setSearchSummary] = useState('Where to? · Any dates · Guests');
    const siteData = useSiteData();

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    // Listen for search dock events from homepage
    useEffect(() => {
        const handleSearchDock = (e) => {
            setSearchDocked(e.detail.docked);
            if (e.detail.summary) {
                setSearchSummary(e.detail.summary);
            }
        };
        window.addEventListener('searchDockChange', handleSearchDock);
        return () => window.removeEventListener('searchDockChange', handleSearchDock);
    }, []);

    const handleDockedSearchClick = () => {
        // Scroll back to top to reveal the search form
        window.scrollTo({ top: 0, behavior: 'smooth' });
        // Dispatch event to open the search form
        window.dispatchEvent(new CustomEvent('openHeroSearch'));
    };

    const navLinks = [
        { href: '/', label: 'Home', key: 'home' },
        { href: '/properties', label: 'Properties', key: 'properties' },
        { href: '/about', label: 'About', key: 'about' },
        { href: '/my-bookings', label: 'My Bookings', key: 'bookings' }
    ];

    const isActive = (key) => {
        if (activePage) return activePage === key;
        const path = siteData.currentPath || window.location.pathname;
        if (key === 'home') return path === '/';
        if (key === 'properties') return path.startsWith('/properties') || path.startsWith('/property/');
        if (key === 'about') return path === '/about' || path === '/about/';
        if (key === 'bookings') return path === '/my-bookings' || path === '/my-bookings/';
        return false;
    };

    return (
        <header className={`header ${scrolled ? 'scrolled' : ''} ${searchDocked ? 'search-docked' : ''}`} id="header">
            <div className="container header__inner">
                <a href="/" aria-label={`${siteData.siteName} — Home`} className="logo-link">
                    <span className="logo-text">{siteData.siteName}</span>
                </a>
                
                {/* Docked Search Bar - appears when scrolled */}
                <button 
                    className={`header__docked-search ${searchDocked ? 'visible' : ''}`}
                    onClick={handleDockedSearchClick}
                    aria-label="Open search"
                >
                    <span className="docked-search__text">{searchSummary}</span>
                    <span className="docked-search__icon">
                        <Icons.Search />
                    </span>
                </button>
                
                <button 
                    className={`mobile-menu-toggle ${menuOpen ? 'active' : ''}`}
                    aria-label="Toggle menu" 
                    aria-expanded={menuOpen}
                    onClick={() => setMenuOpen(!menuOpen)}
                >
                    <span></span>
                    <span></span>
                    <span></span>
                </button>

                <nav className={`header__nav ${menuOpen ? 'open' : ''}`} id="header-nav">
                    <ul className="nav-list">
                        {navLinks.map(link => (
                            <li key={link.key}>
                                <a 
                                    href={link.href} 
                                    className={`nav-link ${isActive(link.key) ? 'active' : ''}`}
                                >
                                    {link.label}
                                </a>
                            </li>
                        ))}
                    </ul>
                    <div className="header__ctas">
                        {siteData.contactPhone && (
                            <a href={`tel:${siteData.contactPhone}`} className="btn btn--outline">
                                <Icons.Phone />
                                <span>{siteData.contactPhone}</span>
                            </a>
                        )}
                        <a href="/properties" className="btn btn--primary">
                            Book Now
                        </a>
                    </div>
                </nav>
            </div>
        </header>
    );
};

// ============================================================================
// FOOTER COMPONENT
// ============================================================================

const Footer = () => {
    const siteData = useSiteData();
    const currentYear = new Date().getFullYear();

    const handleContactClick = (e) => {
        e.preventDefault();
        // Trigger contact modal if it exists
        const event = new CustomEvent('openContactModal');
        document.dispatchEvent(event);
    };

    return (
        <footer className="footer compact-footer">
            <div className="container">
                <div className="footer__inner">
                    <div className="footer__top">
                        <div className="footer__brand">
                            <span className="footer__logo">{siteData.siteName}</span>
                        </div>
                        <div className="footer__mobile-actions">
                            <a href="/properties" className="btn btn--primary btn--sm">Book Now</a>
                        </div>
                    </div>
                    
                    <div className="footer__nav-wrapper">
                        <nav className="footer__nav desktop">
                            <a href="/">Home</a>
                            <a href="/properties">Properties</a>
                            <a href="/about">About Us</a>
                            <a href="#" onClick={handleContactClick}>Contact</a>
                            <a href="/my-bookings">My Bookings</a>
                        </nav>
                    </div>

                    <div className="footer__bottom-row">
                        <div className="footer__contact-inline">
                            {siteData.contactPhone && (
                                <a href={`tel:${siteData.contactPhone}`}>{siteData.contactPhone}</a>
                            )}
                            {siteData.contactPhone && siteData.contactEmail && (
                                <span className="divider">|</span>
                            )}
                            {siteData.contactEmail && (
                                <a href={`mailto:${siteData.contactEmail}`}>{siteData.contactEmail}</a>
                            )}
                        </div>
                        <div className="footer__copyright">
                            © {currentYear} {siteData.siteName}
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    );
};

// ============================================================================
// PROPERTY CARD COMPONENT
// ============================================================================

const PropertyCard = ({ property, variant = 'default' }) => {
    const [liked, setLiked] = useState(false);
    const [imageLoaded, setImageLoaded] = useState(false);

    const handleLike = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setLiked(!liked);
    };

    return (
        <a 
            href={`/property/${property.slug}/`} 
            className={`property-card property-card--${variant} ${imageLoaded ? 'loaded' : ''}`}
        >
            <div className="property-card__image-wrapper">
                <img 
                    src={property.image} 
                    alt={property.title}
                    className="property-card__image"
                    loading="lazy"
                    onLoad={() => setImageLoaded(true)}
                />
                <button 
                    className={`property-card__like ${liked ? 'active' : ''}`}
                    onClick={handleLike}
                    aria-label={liked ? 'Remove from favorites' : 'Add to favorites'}
                >
                    <Icons.Heart filled={liked} />
                </button>
                {property.badge && (
                    <span className="property-card__badge">{property.badge}</span>
                )}
            </div>
            <div className="property-card__content">
                <div className="property-card__location">
                    <Icons.Location />
                    <span>{property.location}</span>
                </div>
                <h3 className="property-card__title">{property.title}</h3>
                <div className="property-card__features">
                    <span><Icons.Bed /> {property.bedrooms} Bed</span>
                    <span><Icons.Bath /> {property.bathrooms} Bath</span>
                    <span><Icons.Users /> {property.guests} Guests</span>
                </div>
                {property.rating && (
                    <div className="property-card__rating">
                        <Icons.Star filled />
                        <span>{property.rating}</span>
                        <span className="property-card__reviews">({property.reviewCount} reviews)</span>
                    </div>
                )}
                <div className="property-card__footer">
                    <div className="property-card__price">
                        <span className="property-card__price-amount">£{property.pricePerNight}</span>
                        <span className="property-card__price-unit">/night</span>
                    </div>
                    <span className="property-card__cta">View Details <Icons.ArrowRight /></span>
                </div>
            </div>
        </a>
    );
};

// ============================================================================
// HERO SECTION COMPONENT
// ============================================================================

const HeroSection = ({ 
    title, 
    subtitle, 
    label, 
    videoSrc, 
    imageSrc,
    height = 'full',
    children,
    centered = false
}) => {
    return (
        <section className={`hero hero--${height}`} id="hero">
            {videoSrc && (
                <video className="hero__bg-video" autoPlay muted loop playsInline>
                    <source src={videoSrc} type="video/mp4" />
                </video>
            )}
            {imageSrc && !videoSrc && (
                <div 
                    className="hero__bg-image" 
                    style={{ backgroundImage: `url(${imageSrc})` }}
                />
            )}
            <div className="hero__overlay"></div>
            
            <div className="container hero__layout">
                <div className={`hero__content fade-in-up ${centered ? 'hero__content--centered' : ''}`}>
                    {label && <span className="hero__label">{label}</span>}
                    {title && <h1 dangerouslySetInnerHTML={{ __html: title }} />}
                    {subtitle && <p className="hero__subhead">{subtitle}</p>}
                    {children}
                </div>
            </div>
        </section>
    );
};

// ============================================================================
// BOOKING FORM COMPONENT
// ============================================================================

const BookingWidget = ({ propertyId, pricePerNight, minNights = 1, maxGuests }) => {
    const [checkIn, setCheckIn] = useState('');
    const [checkOut, setCheckOut] = useState('');
    const [guests, setGuests] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const today = new Date().toISOString().split('T')[0];
    
    const calculateNights = () => {
        if (!checkIn || !checkOut) return 0;
        const start = new Date(checkIn);
        const end = new Date(checkOut);
        const diff = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
        return diff > 0 ? diff : 0;
    };

    const nights = calculateNights();
    const subtotal = nights * pricePerNight;
    const serviceFee = Math.round(subtotal * 0.05);
    const total = subtotal + serviceFee;

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (nights < minNights) {
            setError(`Minimum stay is ${minNights} night${minNights > 1 ? 's' : ''}`);
            return;
        }
        setLoading(true);
        setError('');
        
        // Submit booking - this would typically make an API call
        window.location.href = `/book/${propertyId}/?check_in=${checkIn}&check_out=${checkOut}&guests=${guests}`;
    };

    return (
        <div className="booking-widget">
            <div className="booking-widget__header">
                <div className="booking-widget__price">
                    <span className="booking-widget__price-amount">£{pricePerNight}</span>
                    <span className="booking-widget__price-unit">/night</span>
                </div>
            </div>
            
            <form onSubmit={handleSubmit} className="booking-widget__form">
                <div className="booking-widget__dates">
                    <div className="booking-widget__field">
                        <label>Check-in</label>
                        <input 
                            type="date" 
                            value={checkIn}
                            onChange={(e) => setCheckIn(e.target.value)}
                            min={today}
                            required
                        />
                    </div>
                    <div className="booking-widget__field">
                        <label>Check-out</label>
                        <input 
                            type="date" 
                            value={checkOut}
                            onChange={(e) => setCheckOut(e.target.value)}
                            min={checkIn || today}
                            required
                        />
                    </div>
                </div>
                
                <div className="booking-widget__field">
                    <label>Guests</label>
                    <select 
                        value={guests} 
                        onChange={(e) => setGuests(Number(e.target.value))}
                    >
                        {[...Array(maxGuests || 6)].map((_, i) => (
                            <option key={i + 1} value={i + 1}>
                                {i + 1} Guest{i > 0 ? 's' : ''}
                            </option>
                        ))}
                    </select>
                </div>
                
                {error && <div className="booking-widget__error">{error}</div>}
                
                <button 
                    type="submit" 
                    className="btn btn--primary btn--block"
                    disabled={loading || nights < 1}
                >
                    {loading ? <Icons.Loading /> : 'Reserve'}
                </button>
                
                {nights > 0 && (
                    <div className="booking-widget__summary">
                        <div className="booking-widget__row">
                            <span>£{pricePerNight} × {nights} night{nights > 1 ? 's' : ''}</span>
                            <span>£{subtotal}</span>
                        </div>
                        <div className="booking-widget__row">
                            <span>Service fee</span>
                            <span>£{serviceFee}</span>
                        </div>
                        <div className="booking-widget__row booking-widget__total">
                            <span>Total</span>
                            <span>£{total}</span>
                        </div>
                    </div>
                )}
            </form>
        </div>
    );
};

// ============================================================================
// REVIEW CARD COMPONENT
// ============================================================================

const ReviewCard = ({ review }) => {
    return (
        <div className="review-card">
            <div className="review-card__stars">
                {[...Array(5)].map((_, i) => (
                    <Icons.Star key={i} filled={i < review.rating} />
                ))}
            </div>
            <p className="review-card__text">"{review.text}"</p>
            <div className="review-card__author">
                <strong>- {review.author}</strong>
                {review.role && <span>{review.role}</span>}
            </div>
        </div>
    );
};

// ============================================================================
// BENEFIT CARD COMPONENT
// ============================================================================

const BenefitCard = ({ icon, title, description }) => {
    const IconComponent = Icons[icon] || Icons.Check;
    
    return (
        <div className="benefit-item">
            <div className="benefit-icon">
                <IconComponent />
            </div>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
    );
};

// ============================================================================
// SEARCH FILTER COMPONENT
// ============================================================================

const SearchFilter = ({ onSearch, initialValues = {} }) => {
    const [checkIn, setCheckIn] = useState(initialValues.checkIn || '');
    const [checkOut, setCheckOut] = useState(initialValues.checkOut || '');
    const [guests, setGuests] = useState(initialValues.guests || '');
    const [beds, setBeds] = useState(initialValues.beds || '');

    const today = new Date().toISOString().split('T')[0];

    const handleSubmit = (e) => {
        e.preventDefault();
        if (onSearch) {
            onSearch({ checkIn, checkOut, guests, beds });
        } else {
            // Default: update URL params
            const params = new URLSearchParams();
            if (checkIn) params.set('check_in', checkIn);
            if (checkOut) params.set('check_out', checkOut);
            if (guests) params.set('guests', guests);
            if (beds) params.set('beds', beds);
            window.location.href = `/properties/?${params.toString()}`;
        }
    };

    return (
        <form className="filter-form" onSubmit={handleSubmit}>
            <div className="filter-form__group">
                <label htmlFor="check-in">Check-in</label>
                <input 
                    type="date" 
                    id="check-in" 
                    value={checkIn}
                    onChange={(e) => setCheckIn(e.target.value)}
                    min={today}
                />
            </div>
            <div className="filter-form__group">
                <label htmlFor="check-out">Check-out</label>
                <input 
                    type="date" 
                    id="check-out" 
                    value={checkOut}
                    onChange={(e) => setCheckOut(e.target.value)}
                    min={checkIn || today}
                />
            </div>
            <div className="filter-form__group">
                <label htmlFor="guests">Guests</label>
                <select 
                    id="guests" 
                    value={guests}
                    onChange={(e) => setGuests(e.target.value)}
                >
                    <option value="">Any</option>
                    {[1,2,3,4,5,6].map(n => (
                        <option key={n} value={n}>{n} Guest{n > 1 ? 's' : ''}</option>
                    ))}
                </select>
            </div>
            <div className="filter-form__group">
                <label htmlFor="beds">Bedrooms</label>
                <select 
                    id="beds" 
                    value={beds}
                    onChange={(e) => setBeds(e.target.value)}
                >
                    <option value="">Any</option>
                    {[1,2,3,4,5].map(n => (
                        <option key={n} value={n}>{n} Bedroom{n > 1 ? 's' : ''}</option>
                    ))}
                </select>
            </div>
            <button type="submit" className="btn btn--primary filter-form__submit">
                <Icons.Search />
                Search
            </button>
        </form>
    );
};

// ============================================================================
// BOOKING CARD COMPONENT (for My Bookings page)
// ============================================================================

const BookingCard = ({ booking, onClick }) => {
    const getStatusClass = (status) => {
        const statusMap = {
            'confirmed': 'success',
            'pending': 'warning',
            'cancelled': 'danger',
            'completed': 'info'
        };
        return statusMap[status.toLowerCase()] || 'default';
    };

    return (
        <div className="booking-card" onClick={() => onClick && onClick(booking)}>
            <img 
                src={booking.propertyImage} 
                alt={booking.propertyTitle}
                className="booking-image"
            />
            <div className="booking-details">
                <div className="booking-header">
                    <h3>{booking.propertyTitle}</h3>
                    <span className={`booking-status booking-status--${getStatusClass(booking.status)}`}>
                        {booking.status}
                    </span>
                </div>
                <div className="booking-dates">
                    <Icons.Calendar />
                    <span>{booking.checkIn} → {booking.checkOut}</span>
                </div>
                <div className="booking-info">
                    <span><Icons.Users /> {booking.guests} Guest{booking.guests > 1 ? 's' : ''}</span>
                    <span className="booking-price">£{booking.total}</span>
                </div>
            </div>
        </div>
    );
};

// ============================================================================
// IMAGE GALLERY COMPONENT
// ============================================================================

const ImageGallery = ({ images, title }) => {
    const [activeIndex, setActiveIndex] = useState(0);
    const [showLightbox, setShowLightbox] = useState(false);

    if (!images || images.length === 0) return null;

    return (
        <>
            <div className="image-gallery">
                <div className="image-gallery__main">
                    <img 
                        src={images[activeIndex]} 
                        alt={`${title} - Image ${activeIndex + 1}`}
                        onClick={() => setShowLightbox(true)}
                    />
                </div>
                {images.length > 1 && (
                    <div className="image-gallery__thumbnails">
                        {images.map((img, idx) => (
                            <button
                                key={idx}
                                className={`image-gallery__thumb ${idx === activeIndex ? 'active' : ''}`}
                                onClick={() => setActiveIndex(idx)}
                            >
                                <img src={img} alt={`${title} - Thumbnail ${idx + 1}`} />
                            </button>
                        ))}
                    </div>
                )}
            </div>
            
            {showLightbox && (
                <div className="lightbox" onClick={() => setShowLightbox(false)}>
                    <button className="lightbox__close">
                        <Icons.Close />
                    </button>
                    <img src={images[activeIndex]} alt={title} />
                    {images.length > 1 && (
                        <div className="lightbox__nav">
                            <button 
                                onClick={(e) => { 
                                    e.stopPropagation(); 
                                    setActiveIndex((activeIndex - 1 + images.length) % images.length);
                                }}
                            >
                                ←
                            </button>
                            <span>{activeIndex + 1} / {images.length}</span>
                            <button 
                                onClick={(e) => { 
                                    e.stopPropagation(); 
                                    setActiveIndex((activeIndex + 1) % images.length);
                                }}
                            >
                                →
                            </button>
                        </div>
                    )}
                </div>
            )}
        </>
    );
};

// ============================================================================
// LOADING SPINNER COMPONENT
// ============================================================================

const LoadingSpinner = ({ size = 'medium', text }) => {
    return (
        <div className={`loading-spinner loading-spinner--${size}`}>
            <Icons.Loading />
            {text && <span>{text}</span>}
        </div>
    );
};

// ============================================================================
// TOAST NOTIFICATION COMPONENT
// ============================================================================

const ToastContainer = () => {
    const [toasts, setToasts] = useState([]);

    useEffect(() => {
        const handleToast = (e) => {
            const { message, type = 'info', duration = 3000 } = e.detail;
            const id = Date.now();
            setToasts(prev => [...prev, { id, message, type }]);
            setTimeout(() => {
                setToasts(prev => prev.filter(t => t.id !== id));
            }, duration);
        };

        window.addEventListener('showToast', handleToast);
        return () => window.removeEventListener('showToast', handleToast);
    }, []);

    return (
        <div className="toast-container">
            {toasts.map(toast => (
                <div key={toast.id} className={`toast toast--${toast.type}`}>
                    {toast.message}
                </div>
            ))}
        </div>
    );
};

// Helper function to show toasts
window.showToast = (message, type = 'info', duration = 3000) => {
    window.dispatchEvent(new CustomEvent('showToast', { 
        detail: { message, type, duration } 
    }));
};

// ============================================================================
// CONTACT MODAL COMPONENT
// ============================================================================

const ContactModal = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        message: ''
    });
    const [loading, setLoading] = useState(false);
    const siteData = useSiteData();

    useEffect(() => {
        const handleOpen = () => setIsOpen(true);
        document.addEventListener('openContactModal', handleOpen);
        return () => document.removeEventListener('openContactModal', handleOpen);
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        setLoading(false);
        setIsOpen(false);
        window.showToast('Message sent successfully!', 'success');
        setFormData({ name: '', email: '', phone: '', message: '' });
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={() => setIsOpen(false)}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <button className="modal__close" onClick={() => setIsOpen(false)}>
                    <Icons.Close />
                </button>
                <h2>Contact Us</h2>
                <p>Get in touch with {siteData.siteName}</p>
                
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Name</label>
                        <input 
                            type="text" 
                            value={formData.name}
                            onChange={e => setFormData({...formData, name: e.target.value})}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Email</label>
                        <input 
                            type="email" 
                            value={formData.email}
                            onChange={e => setFormData({...formData, email: e.target.value})}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Phone (optional)</label>
                        <input 
                            type="tel" 
                            value={formData.phone}
                            onChange={e => setFormData({...formData, phone: e.target.value})}
                        />
                    </div>
                    <div className="form-group">
                        <label>Message</label>
                        <textarea 
                            value={formData.message}
                            onChange={e => setFormData({...formData, message: e.target.value})}
                            rows="4"
                            required
                        />
                    </div>
                    <button type="submit" className="btn btn--primary btn--block" disabled={loading}>
                        {loading ? <Icons.Loading /> : 'Send Message'}
                    </button>
                </form>
            </div>
        </div>
    );
};

// ============================================================================
// INITIALIZE GLOBAL COMPONENTS
// ============================================================================

// Auto-mount Header if container exists
const headerRoot = document.getElementById('react-header');
if (headerRoot) {
    const activePage = headerRoot.dataset.activePage;
    ReactDOM.createRoot(headerRoot).render(
        <SiteContext.Provider value={window.SITE_DATA || {}}>
            <Header activePage={activePage} />
        </SiteContext.Provider>
    );
}

// Auto-mount Footer if container exists
const footerRoot = document.getElementById('react-footer');
if (footerRoot) {
    ReactDOM.createRoot(footerRoot).render(
        <SiteContext.Provider value={window.SITE_DATA || {}}>
            <Footer />
        </SiteContext.Provider>
    );
}

// Mount Toast Container
const toastRoot = document.createElement('div');
toastRoot.id = 'toast-root';
document.body.appendChild(toastRoot);
ReactDOM.createRoot(toastRoot).render(<ToastContainer />);

// Mount Contact Modal
const contactModalRoot = document.createElement('div');
contactModalRoot.id = 'contact-modal-root';
document.body.appendChild(contactModalRoot);
ReactDOM.createRoot(contactModalRoot).render(
    <SiteContext.Provider value={window.SITE_DATA || {}}>
        <ContactModal />
    </SiteContext.Provider>
);

// Export components for page-specific use
window.SafeLetComponents = {
    Header,
    Footer,
    PropertyCard,
    HeroSection,
    BookingWidget,
    ReviewCard,
    BenefitCard,
    SearchFilter,
    BookingCard,
    ImageGallery,
    LoadingSpinner,
    ToastContainer,
    ContactModal,
    Icons,
    SiteContext,
    useSiteData
};

console.log('✅ Safe Let Stays React Components loaded');
