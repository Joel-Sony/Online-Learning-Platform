import { useState, useEffect, useRef } from 'react';
import api from '../api';

export const useNotifications = () => {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const socketRef = useRef(null);

    const fetchNotifications = async () => {
        try {
            const res = await api.get('/notifications/');
            setNotifications(res.data);
            setUnreadCount(res.data.filter(n => !n.is_read).length);
        } catch (err) {
            console.error('Failed to fetch notifications:', err);
        }
    };

    useEffect(() => {
        fetchNotifications();

        const token = localStorage.getItem('access');
        if (token) {
            const wsBaseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8001';
            const socketUrl = `${wsBaseUrl}/ws/notifications/?token=${token}`;
            socketRef.current = new WebSocket(socketUrl);

            socketRef.current.onmessage = (event) => {
                const newNotification = JSON.parse(event.data);
                setNotifications((prev) => [newNotification, ...prev]);
                setUnreadCount((prev) => prev + 1);
            };

            socketRef.current.onerror = (err) => console.error('WebSocket Error:', err);
        }

        return () => {
            if (socketRef.current) socketRef.current.close();
        };
    }, []);

    const markAsRead = async (id) => {
        try {
            await api.post(`/notifications/${id}/read/`);
            setNotifications((prev) =>
                prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
            );
            setUnreadCount((prev) => Math.max(0, prev - 1));
        } catch (err) {
            console.error('Failed to mark as read:', err);
        }
    };

    const markAllRead = async () => {
        try {
            await api.post('/notifications/read-all/');
            setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
            setUnreadCount(0);
        } catch (err) {
            console.error('Failed to mark all as read:', err);
        }
    };

    return {
        notifications,
        unreadCount,
        markAsRead,
        markAllRead
    };
};
