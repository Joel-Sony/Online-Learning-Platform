import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import api from '../api';

/* ── Skeleton Card ──────────────────────────────────────────── */
function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton" style={{ paddingTop: '56.25%', width: '100%' }} />
      <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <div className="skeleton" style={{ height: '10px', width: '70px', borderRadius: '20px' }} />
        <div className="skeleton" style={{ height: '16px', width: '100%' }} />
        <div className="skeleton" style={{ height: '16px', width: '75%' }} />
        <div className="skeleton" style={{ height: '12px', width: '55%' }} />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
          <div className="skeleton" style={{ height: '12px', width: '60px' }} />
          <div className="skeleton" style={{ height: '12px', width: '40px' }} />
        </div>
      </div>
    </div>
  );
}

/* ── Course Card ────────────────────────────────────────────── */
function CourseCard({ course }) {
  const [hovered, setHovered] = useState(false);

  const getLevelBadgeStyle = (level) => {
    switch(level) {
      case 'BEGINNER': return { background: '#f0fdf4', color: '#16a34a' };
      case 'INTERMEDIATE': return { background: '#fffbeb', color: '#d97706' };
      case 'ADVANCED': return { background: '#fef2f2', color: '#dc2626' };
      default: return { background: 'var(--surface)', color: 'var(--text-secondary)' };
    }
  };

  const levelLabel = { BEGINNER: 'Beginner', INTERMEDIATE: 'Intermediate', ADVANCED: 'Advanced' }[course.level] || course.level;

  return (
    <Link
      to={`/courses/${course.id}`}
      className="course-card"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Thumbnail */}
      <div className="course-card-thumb">
        {course.thumbnail ? (
          <img src={course.thumbnail} alt={course.title} />
        ) : (
          <div className="course-card-thumb-placeholder">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
          </div>
        )}
        {/* Level badge overlay */}
        <div style={{
          position: 'absolute', top: '10px', left: '10px',
          ...getLevelBadgeStyle(course.level),
          fontSize: '0.7rem', fontWeight: '600',
          padding: '3px 9px', borderRadius: 'var(--radius-pill)',
        }}>
          {levelLabel}
        </div>
        {/* Hover view button */}
        <div style={{
          position: 'absolute', inset: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: 'rgba(0,0,0,0.35)',
          opacity: hovered ? 1 : 0,
          transition: 'opacity 0.25s ease',
        }}>
          <span style={{
            background: '#fff', color: 'var(--text-primary)',
            padding: '8px 18px', borderRadius: 'var(--radius-pill)',
            fontSize: '0.8rem', fontWeight: '600',
            boxShadow: 'var(--shadow-md)',
          }}>
            View Course →
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="course-card-body">
        <span className="badge badge-category" style={{ alignSelf: 'flex-start' }}>
          {course.category}
        </span>

        <h3 className="course-card-title" style={{ marginTop: '6px' }}>
          {course.title}
        </h3>

        {course.description && (
          <p className="course-card-description">
            {course.description}
          </p>
        )}

        <span className="course-card-instructor">
          {course.mentor_name}
        </span>

        {/* Rating */}
        <div className="rating-display" style={{ marginTop: '2px' }}>
          <span className="stars">★★★★★</span>
          <span className="rating-score">{course.avg_rating?.toFixed(1) || '—'}</span>
          {course.enrollment_count > 0 && (
            <span className="rating-count">({course.enrollment_count.toLocaleString()})</span>
          )}
        </div>

        {/* Footer */}
        <div className="course-card-footer">
          <span className="course-card-price">
            {parseFloat(course.price) > 0 ? `$${parseFloat(course.price).toFixed(0)}` : 'Free'}
          </span>
        </div>
      </div>
    </Link>
  );
}

/* ── Filter Sidebar ─────────────────────────────────────────── */
function FilterSidebar({ searchParams, setSearchParams }) {
  const activeCount = Object.fromEntries(searchParams).length;

  const handleFilterChange = (name, value) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) newParams.set(name, value);
    else newParams.delete(name);
    setSearchParams(newParams);
  };

  return (
    <aside className="filter-sidebar">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: '600', color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Filters {activeCount > 0 && <span style={{ color: 'var(--accent)', background: 'var(--accent-light)', borderRadius: '20px', padding: '1px 6px', marginLeft: '4px', fontSize: '0.7rem' }}>{activeCount}</span>}
        </span>
        {activeCount > 0 && (
          <button onClick={() => setSearchParams({})} style={{
            background: 'none', border: 'none', cursor: 'pointer',
            fontSize: '0.78rem', color: 'var(--accent)', fontFamily: 'var(--font-body)',
            padding: '4px 8px', borderRadius: 'var(--radius-sm)',
            transition: 'var(--transition-fast)',
          }}
          onMouseEnter={e => e.currentTarget.style.background = 'var(--accent-light)'}
          onMouseLeave={e => e.currentTarget.style.background = 'none'}
          >
            Clear all
          </button>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Category */}
        <div className="filter-group">
          <div className="filter-group-label">Category</div>
          {['', 'Development', 'Business', 'Design', 'Marketing', 'Music', 'Photography'].map(cat => (
            <button
              key={cat}
              onClick={() => handleFilterChange('category', cat)}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                width: '100%', background: 'none', border: 'none', cursor: 'pointer',
                padding: '8px 10px', borderRadius: 'var(--radius-sm)',
                fontSize: '0.875rem', textAlign: 'left',
                color: searchParams.get('category') === cat ? 'var(--accent)' : 'var(--text-secondary)',
                background: searchParams.get('category') === cat ? 'var(--accent-light)' : 'transparent',
                fontFamily: 'var(--font-body)',
                transition: 'var(--transition-fast)',
                fontWeight: searchParams.get('category') === cat ? '500' : '400',
              }}
              onMouseEnter={e => { if (searchParams.get('category') !== cat) e.currentTarget.style.background = 'var(--surface)'; }}
              onMouseLeave={e => { if (searchParams.get('category') !== cat) e.currentTarget.style.background = 'transparent'; }}
            >
              {cat || 'All Categories'}
              {searchParams.get('category') === cat && (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              )}
            </button>
          ))}
        </div>

        <div style={{ height: '1px', background: 'var(--border)' }} />

        {/* Level */}
        <div className="filter-group">
          <div className="filter-group-label">Level</div>
          <select
            className="filter-select"
            value={searchParams.get('level') || ''}
            onChange={(e) => handleFilterChange('level', e.target.value)}
          >
            <option value="">All Levels</option>
            <option value="BEGINNER">Beginner</option>
            <option value="INTERMEDIATE">Intermediate</option>
            <option value="ADVANCED">Advanced</option>
          </select>
        </div>

        <div style={{ height: '1px', background: 'var(--border)' }} />

        {/* Free only */}
        <label className="filter-checkbox-label" style={{ paddingLeft: '0' }}>
          <input
            type="checkbox"
            checked={searchParams.get('is_free') === 'true'}
            onChange={(e) => handleFilterChange('is_free', e.target.checked ? 'true' : '')}
          />
          Free Courses Only
        </label>

        <div style={{ height: '1px', background: 'var(--border)' }} />

        {/* Sort */}
        <div className="filter-group">
          <div className="filter-group-label">Sort By</div>
          <select
            className="filter-select"
            value={searchParams.get('ordering') || '-created_at'}
            onChange={(e) => handleFilterChange('ordering', e.target.value)}
          >
            <option value="-created_at">Newest First</option>
            <option value="price">Price: Low to High</option>
            <option value="-price">Price: High to Low</option>
            <option value="-avg_rating">Highest Rated</option>
            <option value="-enrollment_count">Most Popular</option>
          </select>
        </div>
      </div>
    </aside>
  );
}

/* ── Empty State ─────────────────────────────────────────────── */
function EmptyState({ query, onClear }) {
  return (
    <div style={{ gridColumn: '1 / -1', padding: '80px 0', textAlign: 'center' }}>
      <div className="empty-state-icon" style={{ margin: '0 auto 20px' }}>
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
      </div>
      <h3 style={{ marginBottom: '8px' }}>No courses found</h3>
      <p style={{ color: 'var(--text-tertiary)', marginBottom: '24px', maxWidth: '380px', margin: '0 auto 24px' }}>
        {query ? `No results for "${query}". Try a different search term or adjust your filters.` : 'No courses match your current filters.'}
      </p>
      <button onClick={onClear} className="btn btn-secondary">Clear Filters</button>
    </div>
  );
}

/* ── Main Component ─────────────────────────────────────────── */
function CourseList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [courses, setCourses] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchInput, setSearchInput] = useState(searchParams.get('search') || '');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestionLoading, setSuggestionLoading] = useState(false);

  const fetchCourses = useCallback(async () => {
    setLoading(true);
    try {
      const params = Object.fromEntries(searchParams);
      if (!params.page) params.page = 1;
      const res = await api.get('/courses/', { params });
      setCourses(res.data.results);
      setTotalCount(res.data.count);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [searchParams]);

  const goToPage = (page) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', page);
    setSearchParams(newParams);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const currentPage = parseInt(searchParams.get('page')) || 1;
  const totalPages = Math.ceil(totalCount / 12);

  useEffect(() => { fetchCourses(); }, [fetchCourses]);

  // Debounced autocomplete
  useEffect(() => {
    if (searchInput.length < 2) {
      setSuggestions([]);
      return;
    }
    setSuggestionLoading(true);
    const timer = setTimeout(async () => {
      try {
        const res = await api.get('/courses/autocomplete/', { params: { q: searchInput } });
        setSuggestions(res.data);
      } catch (e) {
        setSuggestions([]);
      } finally {
        setSuggestionLoading(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const applySearch = (q) => {
    const newParams = new URLSearchParams(searchParams);
    if (q.trim()) newParams.set('search', q);
    else newParams.delete('search');
    setSearchParams(newParams);
    setShowSuggestions(false);
    setSuggestions([]);
  };

  const query = searchParams.get('search') || '';
  const category = searchParams.get('category') || '';

  const pageTitle = query
    ? `Results for "${query}"`
    : category
    ? category
    : 'All Courses';

  return (
    <div style={{ display: 'flex', gap: '48px', padding: '40px 48px', maxWidth: '1280px', margin: '0 auto', width: '100%', alignItems: 'flex-start' }}>
      {/* Sidebar */}
      <FilterSidebar searchParams={searchParams} setSearchParams={setSearchParams} />

      {/* Main */}
      <div style={{ flex: 1, minWidth: 0 }}>
        {/* Page header with inline search */}
        <div style={{ marginBottom: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: '16px' }}>
            <h1 style={{ fontSize: '1.5rem', fontWeight: '600', letterSpacing: '-0.02em' }}>
              {pageTitle}
            </h1>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>
              {loading ? '' : `${totalCount} course${totalCount !== 1 ? 's' : ''}`}
            </span>
          </div>

          {/* Inline search with autocomplete */}
          <form onSubmit={(e) => {
            e.preventDefault();
            applySearch(searchInput);
          }}>
            <div className="search-bar" style={{ maxWidth: '480px', position: 'relative' }}>
              <span className="search-bar-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                </svg>
              </span>
              <input
                name="q"
                value={searchInput}
                onChange={e => { setSearchInput(e.target.value); setShowSuggestions(true); }}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
                className="search-bar-input"
                placeholder="Search courses, instructors, topics..."
                style={{ width: '100%' }}
                autoComplete="off"
              />
              {/* Autocomplete dropdown */}
              {showSuggestions && (suggestions.length > 0 || suggestionLoading) && (
                <div style={{
                  position: 'absolute', top: '100%', left: 0, right: 0, marginTop: '4px',
                  background: 'var(--bg)', border: '1px solid var(--border-strong)',
                  borderRadius: 'var(--radius-md)', boxShadow: 'var(--shadow-lg)',
                  zIndex: 100, overflow: 'hidden',
                }}>
                  {suggestionLoading ? (
                    <div style={{ padding: '12px 16px', fontSize: '0.85rem', color: 'var(--text-tertiary)' }}>Searching...</div>
                  ) : suggestions.map(s => (
                    <button
                      key={s.id}
                      type="button"
                      onMouseDown={() => { setSearchInput(s.title); applySearch(s.title); }}
                      style={{
                        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                        width: '100%', padding: '10px 16px', background: 'none', border: 'none',
                        cursor: 'pointer', textAlign: 'left', fontFamily: 'var(--font-body)',
                        fontSize: '0.875rem', color: 'var(--text-primary)',
                        borderBottom: '1px solid var(--border)',
                        transition: 'background 0.1s',
                      }}
                      onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-subtle)'}
                      onMouseLeave={e => e.currentTarget.style.background = 'none'}
                    >
                      <span>{s.title}</span>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', background: 'var(--surface)', padding: '2px 8px', borderRadius: 'var(--radius-pill)' }}>{s.category}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </form>
        </div>

        {/* Grid */}
        <div className="course-grid">
          {loading
            ? Array(9).fill(0).map((_, i) => <SkeletonCard key={i} />)
            : courses.length > 0
              ? courses.map(c => <CourseCard key={c.id} course={c} />)
              : <EmptyState query={query} onClear={() => setSearchParams({})} />
          }
        </div>

        {/* Pagination */}
        {!loading && totalPages > 1 && (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', marginTop: '32px' }}>
            <button
              className="btn btn-sm btn-secondary"
              disabled={currentPage <= 1}
              onClick={() => goToPage(currentPage - 1)}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 18 9 12 15 6" /></svg>
              Previous
            </button>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-tertiary)', padding: '0 8px' }}>
              Page {currentPage} of {totalPages}
            </span>
            <button
              className="btn btn-sm btn-secondary"
              disabled={currentPage >= totalPages}
              onClick={() => goToPage(currentPage + 1)}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              Next
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6" /></svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default CourseList;
