import React, { ReactNode, useState, useEffect } from 'react';
import { Sidebar, NavPage } from '../components/navigation';
import { Menu } from 'lucide-react';

interface MainLayoutProps {
  children: ReactNode;
  activePage: NavPage;
  onSelectPage: (page: NavPage) => void;
}

export const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  activePage,
  onSelectPage,
}) => {
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);

  // Add CSS rules for desktop vs mobile drawer visibility
  useEffect(() => {
    const styleId = 'responsive-sidebar-rules';
    if (!document.getElementById(styleId)) {
      const style = document.createElement('style');
      style.id = styleId;
      style.innerHTML = `
        @media (max-width: 900px) {
          .desktop-sidebar-only { display: none !important; }
          .mobile-header { display: flex !important; }
        }
        @media (min-width: 901px) {
          .mobile-header { display: none !important; }
          .mobile-drawer-backdrop { display: none !important; }
        }
      `;
      document.head.appendChild(style);
    }
  }, []);

  return (
    <div className="app-container">
      {/* Desktop Sidebar & Mobile Drawer */}
      <Sidebar
        activePage={activePage}
        onSelectPage={onSelectPage}
        isMobileDrawerOpen={isMobileDrawerOpen}
        onCloseMobileDrawer={() => setIsMobileDrawerOpen(false)}
      />

      {/* Main Content Wrapper */}
      <div className="main-content-wrapper">
        {/* Mobile Header Toggle (Only visible < 900px) */}
        <header
          className="mobile-header"
          style={{
            height: '70px',
            borderBottom: '1px solid var(--border-subtle)',
            backgroundColor: 'var(--bg-secondary)',
            display: 'none',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 1.25rem',
            position: 'sticky',
            top: 0,
            zIndex: 30,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <img src="/forge-logo.png" alt="Logo" style={{ width: '28px', height: '28px' }} />
            <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '1.15rem', letterSpacing: '0.04em' }}>
              FORGE
            </span>
          </div>
          <button
            className="forge-btn-secondary"
            onClick={() => setIsMobileDrawerOpen(true)}
            style={{ padding: '0.5rem 0.8rem' }}
          >
            <Menu size={20} />
            <span>Menu</span>
          </button>
        </header>

        {/* Scrollable View Area with subtle top mesh glow */}
        <main className="main-content-scroll" style={{ position: 'relative' }}>
          <div
            style={{
              position: 'absolute',
              top: '-120px',
              right: '15%',
              width: '500px',
              height: '350px',
              background: 'radial-gradient(circle, rgba(212, 175, 99, 0.04) 0%, transparent 70%)',
              pointerEvents: 'none',
              zIndex: 0,
            }}
          />
          <div style={{ position: 'relative', zIndex: 1 }}>
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
