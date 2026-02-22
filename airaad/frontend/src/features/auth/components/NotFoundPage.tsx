import { useNavigate } from 'react-router-dom';
import { Button } from '@/shared/components/dls/Button';
import styles from './NotFoundPage.module.css';

export default function NotFoundPage() {
  const navigate = useNavigate();
  return (
    <div className={styles.page}>
      <span className={styles.code} aria-hidden="true">404</span>
      <h1 className={styles.heading}>Page not found</h1>
      <p className={styles.body}>The page you're looking for doesn't exist or has been moved.</p>
      <Button variant="primary" onClick={() => navigate('/')}>
        Back to Dashboard
      </Button>
    </div>
  );
}
