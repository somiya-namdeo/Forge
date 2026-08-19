import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Home,
  Sparkles,
  Brain,
  BarChart2,
  Trophy,
  Scale,
  BookOpen,
  FileText,
  ChevronLeft,
  ChevronRight,
  Menu
} from 'lucide-react';

export type NavPage =
  | 'home'
  | 'new-architecture'
  | 'decision-engine'
  | 'evaluation'
  | 'benchmark'
  | 'knowledge-base'
  | 'reports';

interface NavItem {
  id: NavPage;
  label: string;
  icon: React.ElementType;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'new-architecture', label: 'New Architecture', icon: Sparkles },
  { id: 'decision-engine', label: 'Decision Engine', icon: Brain },
  { id: 'evaluation', label: 'Evaluation', icon: BarChart2 },
  { id: 'benchmark', label: 'Benchmark', icon: Trophy },
  { id: 'knowledge-base', label: 'Knowledge Base', icon: BookOpen },
  { id: 'reports', label: 'Reports', icon: FileText },
];

interface SidebarProps {
  activePage: NavPage;
  onSelectPage: (page: NavPage) => void;
  isMobileDrawerOpen?: boolean;
  onCloseMobileDrawer?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activePage,
  onSelectPage,
  isMobileDrawerOpen = false,
  onCloseMobileDrawer,
}) => {
  const [collapsed, setCollapsed] = useState<boolean>(() => {
    const saved = localStorage.getItem('forge_sidebar_collapsed');
    return saved ? JSON.parse(saved) : false;
  });

  const [hoveredNav, setHoveredNav] = useState<NavPage | null>(null);

  const toggleCollapse = () => {
    const next = !collapsed;
    setCollapsed(next);
    localStorage.setItem('forge_sidebar_collapsed', JSON.stringify(next));
  };

  const currentWidth = collapsed ? 68 : 240;

  const renderNavList = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem', padding: '0 0.6rem' }}>
      {NAV_ITEMS.map((item) => {
        const isActive = activePage === item.id;
        const isHovered = hoveredNav === item.id;
        const IconComponent = item.icon;

        return (
          <div
            key={item.id}
            style={{ position: 'relative' }}
            onMouseEnter={() => setHoveredNav(item.id)}
            onMouseLeave={() => setHoveredNav(null)}
          >
            <motion.button
              onClick={() => {
                onSelectPage(item.id);
                if (onCloseMobileDrawer) onCloseMobileDrawer();
              }}
              animate={{
                x: !isActive && isHovered ? 4 : 0,
              }}
              transition={{ duration: 0.2 }}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: collapsed ? '0.65rem 0' : '0.6rem 0.9rem',
                justifyContent: collapsed ? 'center' : 'flex-start',
                borderRadius: 'var(--radius-sm)',
                position: 'relative',
                color: isActive ? '#0B0D12' : isHovered ? '#FFFFFF' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.855rem',
                zIndex: 2,
                overflow: 'visible',
              }}
            >
              {isActive && (
                <motion.div
                  layoutId="sidebarActiveIndicator"
                  style={{
                    position: 'absolute',
                    inset: 0,
                    backgroundColor: 'var(--accent-gold)',
                    borderRadius: 'var(--radius-sm)',
                    boxShadow: '0 0 14px rgba(212, 175, 99, 0.35)',
                    zIndex: -1,
                  }}
                  transition={{ type: 'spring', stiffness: 350, damping: 28 }}
                />
              )}
              {!isActive && isHovered && (
                <div
                  style={{
                    position: 'absolute',
                    inset: 0,
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: 'var(--radius-pill)',
                    zIndex: -1,
                  }}
                />
              )}
              <IconComponent
                size={16}
                style={{
                  color: isActive ? '#0B0D12' : isHovered ? 'var(--accent-gold)' : 'inherit',
                  flexShrink: 0,
                  transition: 'color 0.2s',
                }}
              />
              {!collapsed && (
                <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {item.label}
                </span>
              )}
            </motion.button>

            {/* Collapsed Hover Tooltip */}
            {collapsed && isHovered && (
              <motion.div
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.15 }}
                style={{
                  position: 'absolute',
                  left: '58px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  backgroundColor: 'var(--card-bg-elevated)',
                  border: '1px solid var(--border-hover)',
                  color: '#FFFFFF',
                  padding: '0.35rem 0.7rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  boxShadow: '0 4px 15px rgba(0,0,0,0.8)',
                  whiteSpace: 'nowrap',
                  zIndex: 9999,
                  pointerEvents: 'none',
                }}
              >
                {item.label}
              </motion.div>
            )}
          </div>
        );
      })}
    </div>
  );

  const renderUserCard = () => (
    <div
      style={{
        padding: collapsed ? '0.75rem 0' : '0.75rem 1rem',
        borderTop: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: collapsed ? 'center' : 'flex-start',
        gap: '0.65rem',
        backgroundColor: 'rgba(0, 0, 0, 0.2)',
      }}
    >
      <div
        style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #D4AF63 0%, #B89243 100%)',
          color: '#0B0D12',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 700,
          fontSize: '0.75rem',
          flexShrink: 0,
          boxShadow: '0 2px 8px rgba(212, 175, 99, 0.2)',
          cursor: 'pointer',
        }}
        title={collapsed ? 'Alex Engineer — Enterprise v2.4.1' : undefined}
      >
        AE
      </div>
      {!collapsed && (
        <div style={{ overflow: 'hidden' }}>
          <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.82rem', whiteSpace: 'nowrap' }}>
            Alex Engineer
          </div>
          <div style={{ fontSize: '0.71rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <span style={{ color: 'var(--accent-gold)', fontWeight: 600 }}>Enterprise</span>
            <span>·</span>
            <span>v2.4.1</span>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar (Hide on mobile via CSS or media query) */}
      <motion.aside
        animate={{ width: currentWidth }}
        transition={{ type: 'spring', stiffness: 280, damping: 26 }}
        style={{
          height: '100vh',
          backgroundColor: 'var(--bg-secondary)',
          borderRight: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          position: 'sticky',
          top: 0,
          zIndex: 40,
          overflow: 'visible',
          flexShrink: 0,
        }}
        className="desktop-sidebar-only"
      >
        {/* Top Header & Collapse Toggle */}
        <div
          style={{
            height: '60px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: collapsed ? 'center' : 'space-between',
            padding: collapsed ? '0' : '0 1rem 0 1.2rem',
            borderBottom: '1px solid var(--border-subtle)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', cursor: 'pointer' }} onClick={() => onSelectPage('home')}>
            <img src="/forge-logo.png" alt="Forge Logo" style={{ width: '26px', height: '26px', flexShrink: 0 }} />
            {!collapsed && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '1.05rem', letterSpacing: '0.04em', color: '#FFFFFF' }}>
                  FORGE
                </span>
                <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.03em', textTransform: 'uppercase' }}>
                  AI Engineering Platform
                </span>
              </motion.div>
            )}
          </div>

          {!collapsed && (
            <button
              onClick={toggleCollapse}
              className="forge-btn-ghost"
              title="Collapse Sidebar"
              style={{ padding: '0.4rem', color: 'var(--text-muted)' }}
            >
              <ChevronLeft size={18} />
            </button>
          )}
        </div>

        {/* Collapsed top toggle */}
        {collapsed && (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '0.5rem 0' }}>
            <button
              onClick={toggleCollapse}
              className="forge-btn-ghost"
              title="Expand Sidebar (280px)"
              style={{ padding: '0.35rem', color: 'var(--text-muted)' }}
            >
              <ChevronRight size={18} />
            </button>
          </div>
        )}

        {/* Navigation List */}
        <div style={{ flex: 1, padding: '0.75rem 0', overflowY: 'auto', overflowX: 'hidden' }}>
          {renderNavList()}
        </div>

        {/* Bottom User Card */}
        {renderUserCard()}
      </motion.aside>

      {/* Mobile Drawer Backdrop */}
      <AnimatePresence>
        {isMobileDrawerOpen && (
          <div
            style={{
              position: 'fixed',
              inset: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.75)',
              backdropFilter: 'blur(5px)',
              zIndex: 999,
              display: 'flex',
            }}
            onClick={onCloseMobileDrawer}
            className="mobile-drawer-backdrop"
          >
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'spring', stiffness: 320, damping: 30 }}
              style={{
                width: '280px',
                height: '100vh',
                backgroundColor: 'var(--bg-secondary)',
                borderRight: '1px solid var(--border-hover)',
                display: 'flex',
                flexDirection: 'column',
              }}
              onClick={e => e.stopPropagation()}
            >
              <div style={{ height: '60px', display: 'flex', alignItems: 'center', padding: '0 1.2rem', borderBottom: '1px solid var(--border-subtle)', gap: '0.65rem' }}>
                <img src="/forge-logo.png" alt="Forge Logo" style={{ width: '26px', height: '26px' }} />
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '1.05rem', color: '#FFFFFF' }}>FORGE</span>
                  <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>AI Engineering Platform</span>
                </div>
              </div>
              <div style={{ flex: 1, padding: '1.25rem 0', overflowY: 'auto' }}>
                {renderNavList()}
              </div>
              {renderUserCard()}
            </motion.aside>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};
