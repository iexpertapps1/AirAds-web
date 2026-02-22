import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  MapPin,
  Tag,
  Store,
  Upload,
  Camera,
  ShieldCheck,
  BookOpen,
  Users,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useUIStore } from '@/shared/store/uiStore';
import { useAuthStore } from '@/features/auth/store/authStore';
import type { Role } from '@/features/auth/store/authStore';
import styles from './Sidebar.module.css';

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
  allowedRoles: Role[];
}

const NAV_ITEMS: NavItem[] = [
  {
    to: '/',
    label: 'Platform Health',
    icon: <LayoutDashboard size={18} strokeWidth={1.5} />,
    allowedRoles: ['SUPER_ADMIN', 'CITY_MANAGER', 'ANALYST', 'DATA_ENTRY', 'QA_REVIEWER', 'FIELD_AGENT', 'SUPPORT'],
  },
  {
    to: '/geo',
    label: 'Geographic',
    icon: <MapPin size={18} strokeWidth={1.5} />,
    allowedRoles: ['SUPER_ADMIN', 'CITY_MANAGER', 'DATA_ENTRY'],
  },
  {
    to: '/tags',
    label: 'Tags',
    icon: <Tag size={18} strokeWidth={1.5} />,
    allowedRoles: ['SUPER_ADMIN', 'CITY_MANAGER', 'DATA_ENTRY'],
  },
  {
    to: '/vendors',
    label: 'Vendors',
    icon: <Store size={18} strokeWidth={1.5} />,
    allowedRoles: ['SUPER_ADMIN', 'CITY_MANAGER', 'DATA_ENTRY', 'QA_REVIEWER', 'SUPPORT'],
  },
  {
    to: '/imports',
    label: 'Imports',
    icon: <Upload size={18} strokeWidth={1.5} />,
    allowedRoles: ['SUPER_ADMIN', 'CITY_MANAGER', 'DATA_ENTRY'],
  },
  {
    to: '/field-ops',
    label: 'Field Ops',
    icon: <Camera size={18} strokeWidth={1.5} />,
    allowedRoles: ['SUPER_ADMIN', 'CITY_MANAGER', 'FIELD_AGENT'],
  },
  {
    to: '/qa',
    label: 'QA Dashboard',
    icon: <ShieldCheck size={18} strokeWidth={1.5} />,
    allowedRoles: ['SUPER_ADMIN', 'CITY_MANAGER', 'QA_REVIEWER'],
  },
  {
    to: '/system/audit',
    label: 'Audit Log',
    icon: <BookOpen size={18} strokeWidth={1.5} />,
    allowedRoles: ['SUPER_ADMIN', 'ANALYST'],
  },
  {
    to: '/system/users',
    label: 'Users',
    icon: <Users size={18} strokeWidth={1.5} />,
    allowedRoles: ['SUPER_ADMIN'],
  },
];

export function Sidebar() {
  const collapsed = useUIStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const userRole = useAuthStore((s) => s.user?.role);

  const visibleItems = NAV_ITEMS.filter(
    (item) => userRole !== undefined && item.allowedRoles.includes(userRole),
  );

  return (
    <nav
      className={[styles.sidebar, collapsed ? styles.collapsed : ''].join(' ')}
      aria-label="Main navigation"
    >
      <div className={styles.logo} aria-label="AirAd Admin">
        {collapsed ? (
          <span className={styles.logoMark} aria-hidden="true">A</span>
        ) : (
          <span className={styles.logoFull}>AirAd</span>
        )}
      </div>

      <ul className={styles.navList} role="list">
        {visibleItems.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                [styles.navItem, isActive ? styles.navItemActive : ''].join(' ')
              }
              aria-label={collapsed ? item.label : undefined}
            >
              <span className={styles.navIcon} aria-hidden="true">
                {item.icon}
              </span>
              {!collapsed && <span className={styles.navLabel}>{item.label}</span>}
            </NavLink>
          </li>
        ))}
      </ul>

      <button
        className={styles.collapseBtn}
        onClick={toggleSidebar}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        aria-expanded={!collapsed}
      >
        {collapsed ? (
          <ChevronRight size={16} strokeWidth={1.5} aria-hidden="true" />
        ) : (
          <ChevronLeft size={16} strokeWidth={1.5} aria-hidden="true" />
        )}
      </button>
    </nav>
  );
}
