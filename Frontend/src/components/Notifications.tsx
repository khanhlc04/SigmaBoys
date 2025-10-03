import React from 'react';
import { useNotification } from '../contexts/NotificationContext';

export const Notifications: React.FC = () => {
  const { notifications, removeNotification } = useNotification();

  if (notifications.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 space-y-2 z-50">
      {notifications.map(notification => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onRemove={removeNotification}
        />
      ))}
    </div>
  );
};

interface NotificationItemProps {
  notification: {
    id: string;
    message: string;
    type: 'success' | 'error' | 'info';
  };
  onRemove: (id: string) => void;
}

const NotificationItem: React.FC<NotificationItemProps> = ({ notification, onRemove }) => {
  const getNotificationStyles = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-500 border-green-600';
      case 'error':
        return 'bg-red-500 border-red-600';
      case 'info':
      default:
        return 'bg-blue-500 border-blue-600';
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return '✓';
      case 'error':
        return '✕';
      case 'info':
      default:
        return 'ℹ';
    }
  };

  return (
    <div
      className={`
        ${getNotificationStyles(notification.type)}
        text-white px-4 py-3 rounded-lg shadow-lg border-l-4
        min-w-80 max-w-96
        animate-in slide-in-from-right duration-300
        flex items-center space-x-3
        cursor-pointer hover:opacity-90 transition-opacity
      `}
      onClick={() => onRemove(notification.id)}
    >
      <span className="text-lg font-bold">{getIcon(notification.type)}</span>
      <span className="flex-1 text-sm">{notification.message}</span>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onRemove(notification.id);
        }}
        className="text-white hover:text-gray-200 font-bold text-lg leading-none"
      >
        ×
      </button>
    </div>
  );
};