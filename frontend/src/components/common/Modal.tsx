import React, { ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  width?: string | number;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  width = '720px',
}) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1.5rem',
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(6px)',
          }}
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            style={{
              backgroundColor: 'var(--card-bg-elevated)',
              border: '1px solid var(--border-hover)',
              borderRadius: 'var(--radius-card)',
              width: typeof width === 'number' ? `${width}px` : width,
              maxWidth: '100%',
              maxHeight: '85vh',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.9)',
              overflow: 'hidden',
            }}
            onClick={e => e.stopPropagation()}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '1.4rem 1.8rem',
                borderBottom: '1px solid var(--border-subtle)',
              }}
            >
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>{title}</h3>
              <button
                className="forge-btn-ghost"
                onClick={onClose}
                style={{ padding: '0.4rem', borderRadius: '50%' }}
              >
                <X size={20} />
              </button>
            </div>
            <div style={{ padding: '1.8rem', overflowY: 'auto', flex: 1 }}>
              {children}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
