import { useState, useEffect, useRef, useCallback } from 'react';
import api, { getWebSocketUrl } from '../api';
import { isAuthenticated } from '../auth';

export const useNotifications = () => {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const socketRef = useRef(null);
    const reconnectTimerRef = useRef(null);
    const reconnectDelayRef = useRef(1000); // start at 1s, cap at 30s

    const fetchNotifications = async () => {
        try {
            const res = await api.get('/notifications/');
            setNotifications(res.data);
            setUnreadCount(res.data.filter(n => !n.is_read).length);
        } catch (err) {
            console.error('Failed to fetch notifications:', err);
        }
    };

    const connectWebSocket = useCallback(() => {
        const token = localStorage.getItem('access');
        if (!token) return;

        // Don't open a second socket if one is already connecting/open
        if (socketRef.current && socketRef.current.readyState <= WebSocket.OPEN) return;

        const socketUrl = getWebSocketUrl(`/ws/notifications/?token=${token}`);
        const ws = new WebSocket(socketUrl);
        socketRef.current = ws;

        ws.onopen = () => {
            // Reset backoff on successful connection
            reconnectDelayRef.current = 1000;
        };

        ws.onmessage = (event) => {
            try {
                const newNotification = JSON.parse(event.data);
                setNotifications((prev) => [newNotification, ...prev]);
                setUnreadCount((prev) => prev + 1);
            } catch { /* ignore malformed frames */ }
        };

        ws.onerror = (err) => console.error('WebSocket Error:', err);

        ws.onclose = (event) => {
            // Don't reconnect on intentional close (1000) or auth failure (4xxx)
            if (event.code === 1000 || (event.code >= 4000 && event.code < 5000)) return;

            const delay = reconnectDelayRef.current;
            reconnectDelayRef.current = Math.min(delay * 2, 30000); // cap at 30s
            console.warn(`WebSocket closed (${event.code}). Reconnecting in ${delay}ms…`);
            reconnectTimerRef.current = setTimeout(connectWebSocket, delay);
        };
    }, []);

    useEffect(() => {
        if (!isAuthenticated()) return;

        fetchNotifications();
        connectWebSocket();

        return () => {
            clearTimeout(reconnectTimerRef.current);
            if (socketRef.current) {
                socketRef.current.close(1000);
            }
        };
    }, [connectWebSocket]);

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
