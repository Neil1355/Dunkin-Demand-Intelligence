import React, { useState, useEffect } from 'react';

/// <reference types="vite/client" />
import { LayoutDashboard, Pencil, TrendingUp, History, Menu, X, Plus, Trash2, Edit2, Download, QrCode, ClipboardCheck } from 'lucide-react';
// @ts-ignore: third-party module types
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { apiFetch } from '../../utils/api';
import { apiClient } from '../../api/client';
import { ManagerQRCode } from '../../components/ManagerQRCode';
import ExcelUpload from '../../components/ExcelUpload';

interface DashboardProps {
  onLogout: () => void;
  username: string;
  storeId: number;
  donutTypes: string[];
  munchkinTypes: string[];
  onUpdateDonutTypes: (types: string[]) => void;
  onUpdateMunchkinTypes: (types: string[]) => void;
}

export function Dashboard({ onLogout, username, storeId, donutTypes, munchkinTypes, onUpdateDonutTypes, onUpdateMunchkinTypes }: DashboardProps) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    if (typeof window === 'undefined') {
      return true;
    }
    return window.innerWidth >= 1024;
  });
  const [editingItem, setEditingItem] = useState<{ type: 'donut' | 'munchkin'; index: number; value: string } | null>(null);
  const [newItemName, setNewItemName] = useState('');
  const [addingType, setAddingType] = useState<'donut' | 'munchkin' | null>(null);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [forecastPredictions, setForecastPredictions] = useState<any[]>([]);
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [importedData, setImportedData] = useState<any[]>([]);
  const [importedDataLoading, setImportedDataLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<any>({ production: null, waste_pct: null, forecast: null });
  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [weeklyData, setWeeklyData] = useState<any[]>([]);
  const [weeklyDataLoading, setWeeklyDataLoading] = useState(true);
  const [saveLoading, setSaveLoading] = useState(false);
  const [quickStatsData, setQuickStatsData] = useState<any>(null);
  const [quickStatsLoading, setQuickStatsLoading] = useState(true);
  const [productionTrendData, setProductionTrendData] = useState<any[]>([]);
  const [productionTrendLoading, setProductionTrendLoading] = useState(true);
  const [productionFilter, setProductionFilter] = useState<'all' | 'donut' | 'munchkin'>('all');
  const [productionView, setProductionView] = useState<'daily' | 'weekly'>('daily');
  const [importHistoryData, setImportHistoryData] = useState<any[]>([]);
  const [importHistoryLoading, setImportHistoryLoading] = useState(true);
  const [wasteTrendData, setWasteTrendData] = useState<any[]>([]);
  const [wasteTrendLoading, setWasteTrendLoading] = useState(true);
  const [pendingSubmissions, setPendingSubmissions] = useState<any[]>([]);
  const [pendingLoading, setPendingLoading] = useState(true);
  const [pendingError, setPendingError] = useState('');
  const [editingSubmissionId, setEditingSubmissionId] = useState<number | null>(null);
  const [editSubmissionItems, setEditSubmissionItems] = useState<any[]>([]);
  const [editSubmissionNotes, setEditSubmissionNotes] = useState('');
  const [wasteDirectoryProducts, setWasteDirectoryProducts] = useState<any[]>([]);
  const [selectedAddProductId, setSelectedAddProductId] = useState('');
  const [expandedImportedWeeks, setExpandedImportedWeeks] = useState<Record<string, boolean>>({});

  const [quantities, setQuantities] = useState<Record<string, number>>(
    [...donutTypes, ...munchkinTypes].reduce((acc, item) => ({ ...acc, [item]: 0 }), {})
  );

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setSidebarOpen(true);
      } else {
        setSidebarOpen(false);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Fetch dashboard data
  async function fetchDashboardData() {
    try {
      setDashboardLoading(true);
      const today = new Date().toISOString().split('T')[0];
      const result = await apiFetch(`/dashboard/daily?store_id=${storeId}&date=${today}`);
      
      // Calculate totals from result
      const production = result.reduce((sum: number, item: any) => sum + (item.final_quantity || 0), 0);
      const waste = result.reduce((sum: number, item: any) => sum + (item.waste_quantity || 0), 0);
      const waste_pct = production > 0 ? ((waste / production) * 100).toFixed(1) : '0.0';
      
      setDashboardData({ production, waste_pct, forecast: null }); // Forecast loaded separately
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
      setDashboardData({ production: null, waste_pct: null, forecast: null });
    } finally {
      setDashboardLoading(false);
    }
  }

  // Fetch quick stats for KPI cards
  async function fetchQuickStats() {
    try {
      setQuickStatsLoading(true);
      const result = await apiFetch(`/dashboard/quick-stats?store_id=${storeId}`);
      setQuickStatsData({
        ...(result.stats_7d || {}),
        top_waste_products: result.top_waste_products || []
      });
    } catch (err) {
      console.error("Failed to load quick stats:", err);
      setQuickStatsData(null);
    } finally {
      setQuickStatsLoading(false);
    }
  }

  // Fetch production trend data
  async function fetchProductionTrend() {
    try {
      setProductionTrendLoading(true);
      const filterQuery = productionFilter === 'all' ? '' : `&product_type=${productionFilter}`;
      const result = await apiFetch(`/dashboard/production-summary?store_id=${storeId}&days=28${filterQuery}`);
      
      if (result.daily_data && result.daily_data.length > 0) {
        // Use day-level trend for more detail and add a short moving average.
        const sorted = [...result.daily_data].sort((a: any, b: any) =>
          new Date(a.date).getTime() - new Date(b.date).getTime()
        );

        const dailyData = sorted.map((item: any, idx: number, arr: any[]) => {
          const production = Number(item.total_quantity || 0);
          const waste = Number(item.total_waste || 0);
          const products = Number(item.products_produced || 0);
          const optimal = Math.round(production * 0.85);
          const window = arr.slice(Math.max(0, idx - 2), idx + 1);
          const movingAvg = Math.round(
            window.reduce((sum: number, row: any) => sum + Number(row.total_quantity || 0), 0) / window.length
          );

          return {
            day: new Date(item.date).toLocaleDateString('en-US', { month: 'numeric', day: 'numeric' }),
            production,
            waste,
            optimal,
            movingAvg,
            products,
            delta: production - optimal,
          };
        });

        if (productionView === 'weekly') {
          const weeklyGroups: Record<string, any> = {};
          dailyData.forEach((d: any, idx: number) => {
            const week = `Week ${Math.floor(idx / 7) + 1}`;
            if (!weeklyGroups[week]) {
              weeklyGroups[week] = { week, production: 0, waste: 0, optimal: 0, movingAvg: 0, products: 0, count: 0 };
            }
            weeklyGroups[week].production += d.production;
            weeklyGroups[week].waste += d.waste;
            weeklyGroups[week].optimal += d.optimal;
            weeklyGroups[week].products = Math.max(weeklyGroups[week].products, d.products);
            weeklyGroups[week].count += 1;
          });

          const weeklyData = Object.values(weeklyGroups).map((w: any) => ({
            day: w.week,
            production: Math.round(w.production / w.count),
            waste: Math.round(w.waste / w.count),
            optimal: Math.round(w.optimal / w.count),
            movingAvg: Math.round(w.production / w.count),
            products: w.products,
            delta: Math.round((w.production - w.optimal) / w.count),
          }));
          setProductionTrendData(weeklyData.slice(-6));
        } else {
          setProductionTrendData(dailyData.slice(-14));
        }
      } else {
        setProductionTrendData([]);
      }
    } catch (err) {
      console.error("Failed to load production trend:", err);
      setProductionTrendData([]);
    } finally {
      setProductionTrendLoading(false);
    }
  }

  // Fetch waste trend data
  async function fetchWasteTrend() {
    try {
      setWasteTrendLoading(true);
      const result = await apiFetch(`/dashboard/waste-summary?store_id=${storeId}&days=7`);
      
      if (result.daily_data && result.daily_data.length > 0) {
        const wasteChartData = result.daily_data.map((item: any) => ({
          day: new Date(item.date).toLocaleDateString('en-US', { weekday: 'short' }),
          waste: item.waste_percentage || 0,
          sales: 100 - (item.waste_percentage || 0)
        }));
        setWasteTrendData(wasteChartData);
      }
    } catch (err) {
      console.error("Failed to load waste trend:", err);
      setWasteTrendData([]);
    } finally {
      setWasteTrendLoading(false);
    }
  }

  // Fetch recent import history
  async function fetchImportHistory() {
    try {
      setImportHistoryLoading(true);
      const result = await apiFetch(`/dashboard/imports?store_id=${storeId}&days=30`);
      setImportHistoryData(result.imports || []);
    } catch (err) {
      console.error("Failed to load import history:", err);
      setImportHistoryData([]);
    } finally {
      setImportHistoryLoading(false);
    }
  }

  async function fetchWasteDirectoryProducts() {
    const fallbackProducts = [
      ...donutTypes.map((name, index) => ({
        product_id: `donut-${index}-${name}`,
        product_name: name,
        product_type: 'donut'
      })),
      ...munchkinTypes.map((name, index) => ({
        product_id: `munchkin-${index}-${name}`,
        product_name: name,
        product_type: 'munchkin'
      }))
    ];

    try {
      const result = await apiFetch('/anonymous-waste/products');
      if (Array.isArray(result) && result.length > 0) {
        setWasteDirectoryProducts(result);
      } else {
        setWasteDirectoryProducts(fallbackProducts);
      }
    } catch (err) {
      console.error('Failed to load waste directory products:', err);
      setWasteDirectoryProducts(fallbackProducts);
    }
  }

  async function fetchPendingSubmissions() {
    try {
      setPendingLoading(true);
      setPendingError('');
      const result = await apiFetch(`/pending-waste/list?store_id=${storeId}&status=pending`);
      setPendingSubmissions(result.submissions || []);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load pending submissions';
      setPendingError(errorMsg);
      setPendingSubmissions([]);
    } finally {
      setPendingLoading(false);
    }
  }

  async function handleApproveSubmission(submissionId: number) {
    if (!confirm('Approve this submission as-is?')) {
      return;
    }

    try {
      await apiFetch('/pending-waste/approve', {
        method: 'POST',
        body: JSON.stringify({ submission_id: submissionId })
      });
      setPendingSubmissions((prev) => prev.filter((s) => s.id !== submissionId));
      if (editingSubmissionId === submissionId) {
        setEditingSubmissionId(null);
        setEditSubmissionItems([]);
        setEditSubmissionNotes('');
      }
      fetchPendingSubmissions();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Approval failed';
      alert(errorMsg);
    }
  }

  async function handleDiscardSubmission(submissionId: number) {
    const reason = prompt('Discard this submission? Optional reason:') || '';

    try {
      await apiFetch('/pending-waste/discard', {
        method: 'POST',
        body: JSON.stringify({ submission_id: submissionId, reason })
      });
      setPendingSubmissions((prev) => prev.filter((s) => s.id !== submissionId));
      if (editingSubmissionId === submissionId) {
        setEditingSubmissionId(null);
        setEditSubmissionItems([]);
        setEditSubmissionNotes('');
      }
      fetchPendingSubmissions();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Discard failed';
      alert(errorMsg);
    }
  }

  function startEditSubmission(submission: any) {
    setEditingSubmissionId(submission.id);
    setSelectedAddProductId('');
    const originalItems = Array.isArray(submission.items) ? submission.items : [];

    if (originalItems.length > 0) {
      setEditSubmissionItems(
        originalItems.map((item: any) => ({
          product_id: item.product_id ?? null,
          product_name: item.product_name || 'Unnamed Item',
          product_type: item.product_type || 'other',
          waste_quantity: Number(item.waste_quantity) || 0
        }))
      );
    } else {
      const fallbackItems: any[] = [];
      if ((Number(submission.donut_count) || 0) > 0) {
        fallbackItems.push({ product_id: null, product_name: 'Donuts', product_type: 'donut', waste_quantity: Number(submission.donut_count) || 0 });
      }
      if ((Number(submission.munchkin_count) || 0) > 0) {
        fallbackItems.push({ product_id: null, product_name: 'Munchkins', product_type: 'munchkin', waste_quantity: Number(submission.munchkin_count) || 0 });
      }
      if ((Number(submission.other_count) || 0) > 0) {
        fallbackItems.push({ product_id: null, product_name: 'Other', product_type: 'other', waste_quantity: Number(submission.other_count) || 0 });
      }
      setEditSubmissionItems(fallbackItems);
    }

    setEditSubmissionNotes(submission.notes || '');
  }

  function cancelEditSubmission() {
    setEditingSubmissionId(null);
    setEditSubmissionItems([]);
    setEditSubmissionNotes('');
    setSelectedAddProductId('');
  }

  function adjustEditItemQuantity(index: number, delta: number) {
    setEditSubmissionItems((prev) =>
      prev.map((item, itemIndex) =>
        itemIndex === index
          ? { ...item, waste_quantity: Math.max(0, (Number(item.waste_quantity) || 0) + delta) }
          : item
      )
    );
  }

  function addDirectoryItemToEdit() {
    if (!selectedAddProductId) {
      return;
    }

    const selectedProduct = wasteDirectoryProducts.find(
      (product: any) => String(product.product_id) === selectedAddProductId
    );

    if (!selectedProduct) {
      return;
    }

    setEditSubmissionItems((prev) => {
      const existingIndex = prev.findIndex(
        (item: any) =>
          item.product_id === selectedProduct.product_id ||
          (item.product_name === selectedProduct.product_name && item.product_type === selectedProduct.product_type)
      );

      if (existingIndex >= 0) {
        return prev.map((item: any, idx: number) =>
          idx === existingIndex
            ? { ...item, waste_quantity: (Number(item.waste_quantity) || 0) + 1 }
            : item
        );
      }

      return [
        ...prev,
        {
          product_id: selectedProduct.product_id,
          product_name: selectedProduct.product_name,
          product_type: selectedProduct.product_type || 'other',
          waste_quantity: 1
        }
      ];
    });

    setSelectedAddProductId('');
  }

  function getItemAccentColor(productType?: string) {
    if (productType === 'donut') return '#FF671F';
    if (productType === 'munchkin') return '#DA1884';
    return '#8B7355';
  }

  async function saveEditSubmission(submissionId: number) {
    try {
      const response = await apiFetch('/pending-waste/edit-and-save', {
        method: 'POST',
        body: JSON.stringify({
          submission_id: submissionId,
          items: editSubmissionItems.map((item: any) => ({
            product_id: item.product_id,
            product_name: item.product_name,
            product_type: item.product_type,
            waste_quantity: Math.max(0, Number(item.waste_quantity) || 0)
          })),
          notes: editSubmissionNotes || ''
        })
      });
      setPendingSubmissions((prev) => prev.filter((s) => s.id !== submissionId));
      setEditingSubmissionId(null);
      setEditSubmissionItems([]);
      setEditSubmissionNotes('');
      // Show success toast
      alert('✅ Submission edited and saved to daily waste!');
      fetchPendingSubmissions();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Edit failed';
      alert(`❌ ${errorMsg}`);
    }
  }

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setHistoryLoading(true);
        const result = await apiFetch(`/dashboard/waste-summary?store_id=${storeId}&days=7`);
        const normalized = Array.isArray(result?.daily_data)
          ? result.daily_data
              .sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime())
              .map((row: any) => ({
                date: new Date(row.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }),
                production: row.total_produced ?? row.produced ?? 0,
                waste: row.total_waste ?? row.waste ?? 0,
                waste_pct: row.waste_percentage ?? null,
              }))
          : [];
        setHistoryData(normalized);
      } catch (err) {
        console.error("Failed to load history:", err);
        setHistoryData([]);
      } finally {
        setHistoryLoading(false);
      }
    };
    
    const fetchImportedData = async () => {
      try {
        setImportedDataLoading(true);
        const result = await apiFetch(`/throwaway/recent?store_id=${storeId}&days=30`);
        setImportedData(result.weeks || []);
      } catch (err) {
        console.error("Failed to load imported data:", err);
        setImportedData([]);
      } finally {
        setImportedDataLoading(false);
      }
    };
    
    const fetchWeeklyData = async () => {
      try {
        setWeeklyDataLoading(true);
        const result = await apiFetch(`/dashboard/accuracy?store_id=${storeId}&days=7`);
        setWeeklyData(result || []);
      } catch (err) {
        console.error("Failed to load weekly data:", err);
        setWeeklyData([]);
      } finally {
        setWeeklyDataLoading(false);
      }
    };
    
    // Call all fetch functions
    fetchHistory();
    fetchDashboardData();
    fetchWeeklyData();
    fetchForecastPredictions();
    fetchImportedData();
    fetchQuickStats();
    fetchProductionTrend();
    fetchWasteTrend();
    fetchImportHistory();
    fetchWasteDirectoryProducts();
    fetchPendingSubmissions();
  }, [storeId]);

  useEffect(() => {
    fetchProductionTrend();
  }, [storeId, productionFilter, productionView]);

  // Use weekly data for charts if available, otherwise use placeholder
  const wasteData = wasteTrendData.length > 0 
    ? wasteTrendData
    : [
    { day: 'Mon', waste: 0, sales: 0 },
    { day: 'Tue', waste: 0, sales: 0 },
    { day: 'Wed', waste: 0, sales: 0 },
    { day: 'Thu', waste: 0, sales: 0 },
    { day: 'Fri', waste: 0, sales: 0 },
    { day: 'Sat', waste: 0, sales: 0 },
    { day: 'Sun', waste: 0, sales: 0 }
  ];

  const trendData = productionTrendData.length > 0
    ? productionTrendData
    : [
    { day: '3/01', production: 0, waste: 0, optimal: 0, movingAvg: 0, products: 0, delta: 0 },
    { day: '3/02', production: 0, waste: 0, optimal: 0, movingAvg: 0, products: 0, delta: 0 },
    { day: '3/03', production: 0, waste: 0, optimal: 0, movingAvg: 0, products: 0, delta: 0 },
    { day: '3/04', production: 0, waste: 0, optimal: 0, movingAvg: 0, products: 0, delta: 0 }
  ];

  const latestTrendPoint = trendData.length > 0 ? trendData[trendData.length - 1] : null;

  const donutForecasts = forecastPredictions.filter((p: any) =>
    (p.product_type || '').toLowerCase() === 'donut' ||
    ((p.product_name || '').toLowerCase().includes('donut') && !(p.product_name || '').toLowerCase().includes('munchkin'))
  );
  const munchkinForecasts = forecastPredictions.filter((p: any) =>
    (p.product_type || '').toLowerCase() === 'munchkin' ||
    (p.product_name || '').toLowerCase().includes('munchkin')
  );

  const getForecastQty = (product: any) => product.final_quantity || product.predicted_quantity || 0;

  const navItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'data-entry', icon: Pencil, label: 'Enter Daily Data' },
    { id: 'pending-waste', icon: ClipboardCheck, label: 'Pending Waste' },
    { id: 'predictions', icon: TrendingUp, label: 'Predictions' },
    { id: 'history', icon: History, label: 'History' },
    { id: 'imported', icon: Download, label: 'Imported Data' },
    { id: 'qr-code', icon: QrCode, label: 'QR Code' }
  ];

  const handleAddItem = async (type: 'donut' | 'munchkin') => {
    if (!newItemName.trim()) return;

    try {
      // Save to database first
      const response = await apiFetch('/products/create', {
        method: 'POST',
        body: JSON.stringify({ product_name: newItemName.trim() })
      });

      if (response.status === 'success') {
        // Update local state
        if (type === 'donut') {
          onUpdateDonutTypes([...donutTypes, newItemName]);
        } else {
          onUpdateMunchkinTypes([...munchkinTypes, newItemName]);
        }

        setQuantities({ ...quantities, [newItemName]: 0 });
        setNewItemName('');
        setAddingType(null);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to add product';
      alert(`Error adding product: ${errorMsg}`);
      console.error('Product creation error:', err);
    }
  };

  const handleRemoveItem = (type: 'donut' | 'munchkin', index: number) => {
    if (type === 'donut') {
      const newTypes = donutTypes.filter((_, i) => i !== index);
      onUpdateDonutTypes(newTypes);
    } else {
      const newTypes = munchkinTypes.filter((_, i) => i !== index);
      onUpdateMunchkinTypes(newTypes);
    }
  };

  const handleEditItem = (type: 'donut' | 'munchkin', index: number) => {
    const value = type === 'donut' ? donutTypes[index] : munchkinTypes[index];
    setEditingItem({ type, index, value });
  };

  const handleSaveEdit = () => {
    if (!editingItem || !editingItem.value.trim()) return;

    if (editingItem.type === 'donut') {
      const newTypes = [...donutTypes];
      newTypes[editingItem.index] = editingItem.value;
      onUpdateDonutTypes(newTypes);
    } else {
      const newTypes = [...munchkinTypes];
      newTypes[editingItem.index] = editingItem.value;
      onUpdateMunchkinTypes(newTypes);
    }

    setEditingItem(null);
  };

  const handleExportData = async () => {
    try {
      // Prefer exporting the most recently imported week; fallback to previous week (Sunday start).
      let weekStart = '';
      if (Array.isArray(importedData) && importedData.length > 0 && importedData[0]?.week_start) {
        weekStart = String(importedData[0].week_start).slice(0, 10);
      } else {
        const today = new Date();
        const dayOfWeek = today.getDay();
        const daysToSunday = dayOfWeek === 0 ? 7 : dayOfWeek + 7;
        const previousSunday = new Date(today);
        previousSunday.setDate(today.getDate() - daysToSunday);
        weekStart = previousSunday.toISOString().split('T')[0];
      }

      // Call backend export endpoint
      const baseUrl = import.meta.env.VITE_API_URL || 'https://dunkin-demand-intelligence.onrender.com/api/v1';
      const url = `${baseUrl}/throwaway/export?store_id=${storeId}&week_start=${weekStart}`;
      
      // Fetch first to check for errors
      const response = await fetch(url, { credentials: 'include' });
      
      if (!response.ok) {
        // Try to parse error message
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Export failed');
        } else {
          throw new Error(`Export failed: ${response.statusText}`);
        }
      }
      
      // Success - trigger download
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `dunkin_export_${weekStart}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      alert('Export failed: ' + errorMsg);
      console.error('Export error:', err);
    }
  };

  async function handleGenerateForecast() {
    // Show modal instead of prompts
    setShowForecastModal(true);
  }

  async function submitForecastGeneration() {
    setShowForecastModal(false);
    setForecastLoading(true);
    try {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const targetDate = tomorrow.toISOString().split("T")[0];

      // Save context with selected options
      try {
        await apiFetch('/forecast/context/', {
          method: 'POST',
          body: JSON.stringify({
            store_id: storeId,
            target_date: targetDate,
            expectation: forecastBusinessLevel,
            reason: forecastReason,
            notes: forecastNotes,
          }),
        });
      } catch (contextErr) {
        console.warn('Context save failed, continuing forecast generation:', contextErr);
      }
      
      // Generate forecast with adjustment multiplier
      const multiplier = forecastBusinessLevel === 'busy' ? 1.2 : 
                        forecastBusinessLevel === 'slower' ? 0.8 : 1.0;
      
      const result = await apiFetch(
        `/forecast/next-day?store_id=${storeId}&target_date=${targetDate}&adjustment=${multiplier}`
      );
      
      const count = result?.generated_products ?? Object.keys(result?.forecast || {}).length;
      alert(`Forecast generated successfully for ${count} products.`);
      console.log("Forecast result:", result);
      
      // Fetch the generated forecast to display
      await fetchForecastPredictions(targetDate);
      
      // Reset modal state
      setForecastBusinessLevel('normal');
      setForecastReason('regular_day');
      setForecastNotes('');
    } catch (err) {
      alert("Failed to generate forecast: " + (err instanceof Error ? err.message : 'Unknown error'));
      console.error(err);
    } finally {
      setForecastLoading(false);
    }
  }

  async function fetchForecastPredictions(targetDate?: string) {
    try {
      setForecastLoading(true);
      const tomorrow = targetDate || (() => {
        const d = new Date();
        d.setDate(d.getDate() + 1);
        return d.toISOString().split("T")[0];
      })();
      
      const result = await apiFetch(`/forecast?store_id=${storeId}&target_date=${tomorrow}`);
      
      if (result.products) {
        setForecastPredictions(result.products);
        
        // Update dashboard forecast total
        const totalForecast = result.products.reduce((sum: number, p: any) => sum + (p.final_quantity || p.predicted_quantity || 0), 0);
        setDashboardData((prev: any) => ({ ...prev, forecast: totalForecast }));
      } else {
        setForecastPredictions([]);
        setDashboardData((prev: any) => ({ ...prev, forecast: 0 }));
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);

      if (message.toLowerCase().includes("no forecast found")) {
        setForecastPredictions([]);
        setDashboardData((prev: any) => ({ ...prev, forecast: 0 }));
        return;
      }

      console.error("Failed to load forecast predictions:", err);
      setForecastPredictions([]);
    } finally {
      setForecastLoading(false);
    }
  }

  async function handleSaveData() {
    setSaveLoading(true);
    try {
      const today = new Date().toISOString().split("T")[0];
      
      // Fetch all products to get IDs
      const productsList = await apiFetch("/products/list");
      
      // Create name-to-ID mapping
      const productNameMap: Record<string, number> = {};
      productsList.forEach((p: any) => {
        productNameMap[p.product_name.toLowerCase()] = p.product_id;
      });
      
      const items = Object.keys(quantities).map((key) => ({
        name: key,
        produced: quantities[key],
        waste: Math.max(0, Math.floor(quantities[key] * 0.08))
      }));

      let savedCount = 0;
      let errorCount = 0;
      
      for (const item of items) {
        if (item.produced === 0 && item.waste === 0) continue;
        
        const productId = productNameMap[item.name.toLowerCase()];
        
        if (!productId) {
          console.warn(`Product "${item.name}" not found in database, skipping`);
          errorCount++;
          continue;
        }
        
        try {
          await apiFetch("/daily", {
            method: "POST",
            body: JSON.stringify({
              store_id: storeId,
              product_id: productId,
              date: today,
              produced: item.produced,
              waste: item.waste
            })
          });
          savedCount++;
        } catch (err) {
          console.error(`Failed to save ${item.name}:`, err);
          errorCount++;
        }
      }
      
      if (errorCount === 0) {
        alert(`✅ Successfully saved ${savedCount} items!`);
        // Refresh dashboard data
        fetchDashboardData();
      } else {
        alert(`⚠️ Saved ${savedCount} items, ${errorCount} failed. Check console for details.`);
      }
    } catch (err) {
      alert("❌ Failed to save data: " + (err instanceof Error ? err.message : 'Unknown error'));
      console.error('Save error:', err);
    } finally {
      setSaveLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen" style={{ backgroundColor: '#F5F0E8' }}>
      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full w-64 transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 z-30 lg:static lg:translate-x-0`}
        style={{ backgroundColor: '#DA1884' }}
      >
        <div className="p-6">
          <div className="flex items-center gap-2 mb-8">
            <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center">
              <span className="text-xl">🍩</span>
            </div>
            <span className="text-white">DDI</span>
          </div>

          <nav className="space-y-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-2xl transition-all ${activeTab === item.id ? 'bg-white' : 'hover:bg-white/20'
                  }`}
                style={{ color: activeTab === item.id ? '#DA1884' : 'white' }}
              >
                <item.icon size={20} />
                <span>{item.label}</span>
              </button>
            ))}
          </nav>

          <button
            onClick={onLogout}
            className="w-full mt-8 px-4 py-3 rounded-2xl bg-white/20 text-white hover:bg-white/30 transition-all"
          >
            Logout
          </button>
        </div>
      </aside>

      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {/* Top Bar */}
        <div className="bg-white shadow-sm p-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-all"
            >
              {sidebarOpen ? <X size={24} style={{ color: '#FF671F' }} /> : <Menu size={24} style={{ color: '#FF671F' }} />}
            </button>
            <div>
              <div style={{ color: '#FF671F' }}>Store #{storeId}</div>
              <div className="text-sm" style={{ color: '#8B7355' }}>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}</div>
            </div>
          </div>

          <button
            onClick={handleExportData}
            className="flex items-center justify-center gap-2 px-4 py-2 rounded-full text-white transition-all hover:scale-105 w-full sm:w-auto"
            style={{ backgroundColor: '#FF671F' }}
          >
            <Download size={18} />
            Export Data
          </button>
        </div>

        {/* Dashboard Content */}
        <div className="p-4 sm:p-6">
          <div className="mx-auto w-full max-w-6xl">
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Greeting */}
              <div className="bg-gradient-to-r from-orange-50 to-pink-50 rounded-3xl p-6 shadow-lg">
                <h2 style={{ color: '#FF671F' }}>Hey {username}! 👋</h2>
                <p style={{ color: '#8B7355' }}>Welcome back to your Dunkin' Demand Intelligence dashboard.</p>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white rounded-3xl p-6 shadow-lg">
                  <div className="text-sm mb-2" style={{ color: '#8B7355' }}>Total Produced (7d)</div>
                  <div className="text-3xl" style={{ color: '#FF671F' }}>
                    {quickStatsLoading ? '—' : quickStatsData?.total_produced || '0'} {quickStatsData?.total_produced ? 'Units' : ''}
                  </div>
                </div>
                <div className="bg-white rounded-3xl p-6 shadow-lg">
                  <div className="text-sm mb-2" style={{ color: '#8B7355' }}>Waste (7d)</div>
                  <div className="text-3xl" style={{ color: '#DA1884' }}>
                    {quickStatsLoading ? '—' : quickStatsData?.total_waste || '0'} {quickStatsData?.total_waste ? 'Units' : ''}
                  </div>
                </div>
                <div className="bg-white rounded-3xl p-6 shadow-lg">
                  <div className="text-sm mb-2" style={{ color: '#8B7355' }}>Waste Ratio</div>
                  <div className="text-3xl" style={{ color: '#FF671F' }}>
                    {quickStatsLoading ? '—' : `${quickStatsData?.waste_ratio || 0}%`}
                  </div>
                </div>
                <div className="bg-white rounded-3xl p-6 shadow-lg">
                  <div className="text-sm mb-2" style={{ color: '#8B7355' }}>Top Waste Product</div>
                  <div className="text-lg" style={{ color: '#DA1884' }}>
                    {quickStatsLoading ? '—' : quickStatsData?.top_waste_products?.[0]?.product || 'N/A'}
                  </div>
                  <div className="text-sm mt-1" style={{ color: '#8B7355' }}>
                    {quickStatsLoading ? '' : `${quickStatsData?.top_waste_products?.[0]?.waste || 0} units`}
                  </div>
                </div>
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-3xl p-6 shadow-lg">
                  <h3 className="mb-4" style={{ color: '#FF671F' }}>Weekly Waste vs Sales (%)</h3>
                  {wasteTrendLoading ? (
                    <div className="h-[300px] flex items-center justify-center" style={{ color: '#8B7355' }}>
                      Loading chart data...
                    </div>
                  ) : wasteData.length === 0 ? (
                    <div className="h-[300px] flex items-center justify-center" style={{ color: '#8B7355' }}>
                      No data available yet
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={wasteData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E0D5C7" />
                        <XAxis dataKey="day" stroke="#8B7355" />
                        <YAxis stroke="#8B7355" />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="waste" fill="#DA1884" radius={[8, 8, 0, 0]} />
                        <Bar dataKey="sales" fill="#FF671F" radius={[8, 8, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </div>

                <div className="bg-white rounded-3xl p-6 shadow-lg">
                  <h3 className="mb-4" style={{ color: '#FF671F' }}>Production Optimization</h3>
                  <div className="mb-4 flex flex-wrap items-center gap-3">
                    <select
                      value={productionFilter}
                      onChange={(e) => setProductionFilter(e.target.value as 'all' | 'donut' | 'munchkin')}
                      className="px-3 py-2 rounded-lg border"
                      style={{ borderColor: '#FFD7B5', color: '#8B7355' }}
                    >
                      <option value="all">All Products</option>
                      <option value="donut">Donuts Only</option>
                      <option value="munchkin">Munchkins Only</option>
                    </select>
                    <div className="inline-flex rounded-lg overflow-hidden border" style={{ borderColor: '#FFD7B5' }}>
                      <button
                        onClick={() => setProductionView('daily')}
                        className="px-3 py-2 text-sm"
                        style={{ backgroundColor: productionView === 'daily' ? '#FF671F' : '#FFF8F0', color: productionView === 'daily' ? 'white' : '#8B7355' }}
                      >
                        Daily
                      </button>
                      <button
                        onClick={() => setProductionView('weekly')}
                        className="px-3 py-2 text-sm"
                        style={{ backgroundColor: productionView === 'weekly' ? '#FF671F' : '#FFF8F0', color: productionView === 'weekly' ? 'white' : '#8B7355' }}
                      >
                        Weekly
                      </button>
                    </div>
                  </div>
                  {latestTrendPoint && latestTrendPoint.production > 0 && (
                    <p className="text-sm mb-3" style={{ color: '#8B7355' }}>
                      Latest day: {latestTrendPoint.production} produced across {latestTrendPoint.products} products.
                      Waste: {latestTrendPoint.waste || 0}. Target: {latestTrendPoint.optimal} ({latestTrendPoint.delta >= 0 ? '+' : ''}{latestTrendPoint.delta} vs target)
                    </p>
                  )}
                  {productionTrendLoading ? (
                    <div className="h-[300px] flex items-center justify-center" style={{ color: '#8B7355' }}>
                      Loading chart data...
                    </div>
                  ) : trendData.length === 0 || trendData[0].production === 0 ? (
                    <div className="h-[300px] flex items-center justify-center" style={{ color: '#8B7355' }}>
                      No data available yet
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={trendData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E0D5C7" />
                        <XAxis dataKey="day" stroke="#8B7355" />
                        <YAxis stroke="#8B7355" />
                        <Tooltip
                          formatter={(value: any, name: any) => {
                            const labels: Record<string, string> = {
                              production: 'Produced',
                              optimal: 'Target',
                              movingAvg: '3-day Avg',
                              waste: 'Waste'
                            };
                            return [value, labels[String(name)] || String(name)];
                          }}
                        />
                        <Legend />
                        <Line type="monotone" dataKey="production" stroke="#DA1884" strokeWidth={3} />
                        <Line type="monotone" dataKey="optimal" stroke="#FF671F" strokeWidth={3} />
                        <Line type="monotone" dataKey="waste" stroke="#7A4B2A" strokeWidth={2} />
                        <Line type="monotone" dataKey="movingAvg" stroke="#8B7355" strokeDasharray="5 5" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </div>

              {/* Import History */}
              <div className="bg-white rounded-3xl p-6 shadow-lg">
                <h3 className="mb-4" style={{ color: '#FF671F' }}>Recent Imports</h3>
                {importHistoryLoading ? (
                  <div style={{ color: '#8B7355' }}>Loading import history...</div>
                ) : importHistoryData.length === 0 ? (
                  <div style={{ color: '#8B7355' }}>No recent imports found</div>
                ) : (
                  <div className="space-y-3">
                    {importHistoryData.slice(0, 5).map((imp, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 rounded-2xl hover:shadow-md transition-all" style={{ backgroundColor: '#FFF8F0' }}>
                        <div>
                          <p className="font-medium" style={{ color: '#8B7355' }}>
                            {imp.import_type === 'throwaway' ? '📦 Throwaway Data' : '📊 Production Data'}
                          </p>
                          <p className="text-sm" style={{ color: '#8B7355' }}>
                            {new Date(imp.import_date).toLocaleDateString()} - {imp.products_imported} products
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium" style={{ color: '#FF671F' }}>{imp.total_records} records</p>
                          <p className="text-sm" style={{ color: '#8B7355' }}>
                            {imp.total_produced ? `${imp.total_produced} produced` : `${imp.total_quantity || 0} qty`}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'data-entry' && (
            <div className="space-y-6">
              {/* Excel Import Section */}
              <div className="bg-white rounded-3xl p-8 shadow-lg">
                <h3 className="mb-4" style={{ color: '#FF671F' }}>Bulk Import from Excel</h3>
                <p className="mb-6 text-sm" style={{ color: '#8B7355' }}>
                  Upload weekly throwaway sheets with AM/PM production and waste data.
                </p>
                <ExcelUpload storeId={storeId} />
              </div>

              {/* Manual Entry Section */}
              <div className="bg-white rounded-3xl p-8 shadow-lg">
                <h3 className="mb-6" style={{ color: '#FF671F' }}>Manual Daily Input</h3>

                {/* Donuts Section */}
                <div className="space-y-4 mb-8">
                  <div className="flex items-center justify-between">
                    <h4 style={{ color: '#DA1884' }}>Donuts</h4>
                    <button
                      onClick={() => setAddingType('donut')}
                      className="flex items-center gap-2 px-4 py-2 rounded-full text-white transition-all hover:scale-105"
                      style={{ backgroundColor: '#FF671F' }}
                    >
                      <Plus size={18} />
                      Add Donut Type
                    </button>
                  </div>

                  {addingType === 'donut' && (
                    <div className="flex gap-2 p-4 rounded-2xl" style={{ backgroundColor: '#FFF8F0' }}>
                      <input
                        type="text"
                        value={newItemName}
                        onChange={(e) => setNewItemName(e.target.value)}
                        placeholder="Enter donut name..."
                        className="flex-1 px-4 py-2 rounded-full border-2 focus:outline-none"
                        style={{ borderColor: '#FF671F' }}
                        onKeyPress={(e) => e.key === 'Enter' && handleAddItem('donut')}
                      />
                      <button
                        onClick={() => handleAddItem('donut')}
                        className="px-4 py-2 rounded-full text-white"
                        style={{ backgroundColor: '#FF671F' }}
                      >
                        Add
                      </button>
                      <button
                        onClick={() => { setAddingType(null); setNewItemName(''); }}
                        className="px-4 py-2 rounded-full"
                        style={{ backgroundColor: '#E0D5C7', color: '#8B7355' }}
                      >
                        Cancel
                      </button>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {donutTypes.map((donut, index) => (
                      <div key={index} className="flex items-center justify-between p-4 rounded-2xl" style={{ backgroundColor: '#FFF8F0' }}>
                        {editingItem?.type === 'donut' && editingItem.index === index ? (
                          <input
                            type="text"
                            value={editingItem.value}
                            onChange={(e) => setEditingItem({ ...editingItem, value: e.target.value })}
                            className="flex-1 px-3 py-1 rounded-full border-2 focus:outline-none"
                            style={{ borderColor: '#FF671F' }}
                            onKeyPress={(e) => e.key === 'Enter' && handleSaveEdit()}
                            autoFocus
                          />
                        ) : (
                          <span style={{ color: '#8B7355' }}>{donut}</span>
                        )}

                        <div className="flex items-center gap-2">
                          {editingItem?.type === 'donut' && editingItem.index === index ? (
                            <>
                              <button
                                onClick={handleSaveEdit}
                                className="p-1 rounded-lg hover:bg-white transition-all"
                                style={{ color: '#FF671F' }}
                              >
                                Save
                              </button>
                              <button
                                onClick={() => setEditingItem(null)}
                                className="p-1 rounded-lg hover:bg-white transition-all"
                                style={{ color: '#8B7355' }}
                              >
                                Cancel
                              </button>
                            </>
                          ) : (
                            <>
                              <button
                                onClick={() => handleEditItem('donut', index)}
                                className="p-1 rounded-lg hover:bg-white transition-all"
                                style={{ color: '#FF671F' }}
                              >
                                <Edit2 size={16} />
                              </button>
                              <button
                                onClick={() => handleRemoveItem('donut', index)}
                                className="p-1 rounded-lg hover:bg-white transition-all"
                                style={{ color: '#DA1884' }}
                              >
                                <Trash2 size={16} />
                              </button>
                              <input
                                type="number"
                                value={quantities[donut] || 0}
                                onChange={(e) => setQuantities({ ...quantities, [donut]: parseInt(e.target.value) || 0 })}
                                className="w-20 px-3 py-2 rounded-full border-2 text-center focus:outline-none"
                                style={{ borderColor: '#FF671F' }}
                                min="0"
                              />
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Munchkins Section */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 style={{ color: '#DA1884' }}>Munchkins</h4>
                    <button
                      onClick={() => setAddingType('munchkin')}
                      className="flex items-center gap-2 px-4 py-2 rounded-full text-white transition-all hover:scale-105"
                      style={{ backgroundColor: '#DA1884' }}
                    >
                      <Plus size={18} />
                      Add Munchkin Type
                    </button>
                  </div>

                  {addingType === 'munchkin' && (
                    <div className="flex gap-2 p-4 rounded-2xl" style={{ backgroundColor: '#FFF8F0' }}>
                      <input
                        type="text"
                        value={newItemName}
                        onChange={(e) => setNewItemName(e.target.value)}
                        placeholder="Enter munchkin name..."
                        className="flex-1 px-4 py-2 rounded-full border-2 focus:outline-none"
                        style={{ borderColor: '#DA1884' }}
                        onKeyPress={(e) => e.key === 'Enter' && handleAddItem('munchkin')}
                      />
                      <button
                        onClick={() => handleAddItem('munchkin')}
                        className="px-4 py-2 rounded-full text-white"
                        style={{ backgroundColor: '#DA1884' }}
                      >
                        Add
                      </button>
                      <button
                        onClick={() => { setAddingType(null); setNewItemName(''); }}
                        className="px-4 py-2 rounded-full"
                        style={{ backgroundColor: '#E0D5C7', color: '#8B7355' }}
                      >
                        Cancel
                      </button>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {munchkinTypes.map((munchkin, index) => (
                      <div key={index} className="flex items-center justify-between p-4 rounded-2xl" style={{ backgroundColor: '#FFF8F0' }}>
                        {editingItem?.type === 'munchkin' && editingItem.index === index ? (
                          <input
                            type="text"
                            value={editingItem.value}
                            onChange={(e) => setEditingItem({ ...editingItem, value: e.target.value })}
                            className="flex-1 px-3 py-1 rounded-full border-2 focus:outline-none"
                            style={{ borderColor: '#DA1884' }}
                            onKeyPress={(e) => e.key === 'Enter' && handleSaveEdit()}
                            autoFocus
                          />
                        ) : (
                          <span style={{ color: '#8B7355' }}>{munchkin}</span>
                        )}

                        <div className="flex items-center gap-2">
                          {editingItem?.type === 'munchkin' && editingItem.index === index ? (
                            <>
                              <button
                                onClick={handleSaveEdit}
                                className="p-1 rounded-lg hover:bg-white transition-all"
                                style={{ color: '#DA1884' }}
                              >
                                Save
                              </button>
                              <button
                                onClick={() => setEditingItem(null)}
                                className="p-1 rounded-lg hover:bg-white transition-all"
                                style={{ color: '#8B7355' }}
                              >
                                Cancel
                              </button>
                            </>
                          ) : (
                            <>
                              <button
                                onClick={() => handleEditItem('munchkin', index)}
                                className="p-1 rounded-lg hover:bg-white transition-all"
                                style={{ color: '#DA1884' }}
                              >
                                <Edit2 size={16} />
                              </button>
                              <button
                                onClick={() => handleRemoveItem('munchkin', index)}
                                className="p-1 rounded-lg hover:bg-white transition-all"
                                style={{ color: '#FF671F' }}
                              >
                                <Trash2 size={16} />
                              </button>
                              <input
                                type="number"
                                value={quantities[munchkin] || 0}
                                onChange={(e) => setQuantities({ ...quantities, [munchkin]: parseInt(e.target.value) || 0 })}
                                className="w-20 px-3 py-2 rounded-full border-2 text-center focus:outline-none"
                                style={{ borderColor: '#DA1884' }}
                                min="0"
                              />
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <button
                  onClick={handleSaveData}
                  disabled={saveLoading}
                  className="w-full mt-8 py-4 rounded-full text-white transition-opacity disabled:opacity-50"
                  style={{ backgroundColor: '#FF671F' }}
                >
                  {saveLoading ? 'Saving...' : "Save Today's Data"}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'pending-waste' && (
            <div className="space-y-6">
              <div className="bg-white rounded-3xl p-6 shadow-lg">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-4">
                  <h3 style={{ color: '#FF671F' }}>Pending Waste Submissions</h3>
                  <button
                    onClick={fetchPendingSubmissions}
                    className="px-4 py-2 rounded-full text-white transition-all hover:scale-105"
                    style={{ backgroundColor: '#FF671F' }}
                  >
                    Refresh
                  </button>
                </div>
                <p className="mb-6" style={{ color: '#8B7355' }}>
                  Review waste submissions from staff QR scans and approve or discard them.
                </p>

                {pendingLoading ? (
                  <div style={{ color: '#8B7355' }}>Loading pending submissions...</div>
                ) : pendingError ? (
                  <div className="p-4 rounded-2xl" style={{ backgroundColor: '#FFF3F3', color: '#B42318' }}>
                    {pendingError}
                  </div>
                ) : pendingSubmissions.length === 0 ? (
                  <div style={{ color: '#8B7355' }}>No pending submissions right now.</div>
                ) : (
                  <div className="space-y-4">
                    {pendingSubmissions.map((submission) => {
                      const items = submission.items || [];
                      const totalWaste = items.reduce((sum: number, item: any) => sum + (item.waste_quantity || 0), 0);
                      return (
                        <div key={submission.id} className="rounded-2xl p-4 sm:p-6" style={{ backgroundColor: '#FFF8F0' }}>
                          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                            <div>
                              <div className="text-sm" style={{ color: '#8B7355' }}>Submitted by</div>
                              <div className="text-lg" style={{ color: '#DA1884' }}>{submission.submitter_name}</div>
                            </div>
                            <div className="text-sm" style={{ color: '#8B7355' }}>
                              {submission.submitted_at ? new Date(submission.submitted_at).toLocaleString() : 'Unknown time'}
                            </div>
                          </div>

                          {submission.notes && (
                            <div className="mt-3 text-sm" style={{ color: '#8B7355' }}>
                              Notes: {submission.notes}
                            </div>
                          )}

                          <div className="mt-4">
                            <div className="text-sm mb-2" style={{ color: '#8B7355' }}>Items ({totalWaste} units)</div>
                            {items.length === 0 ? (
                              <div className="text-sm" style={{ color: '#8B7355' }}>
                                No item details available for this submission.
                              </div>
                            ) : (
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                {items.map((item: any, idx: number) => (
                                  <div key={`${submission.id}-${idx}`} className="flex items-center justify-between rounded-xl px-3 py-2" style={{ backgroundColor: '#FFFFFF' }}>
                                    <div>
                                      <div style={{ color: '#8B7355' }}>{item.product_name}</div>
                                      <div className="text-xs" style={{ color: '#8B7355' }}>{item.product_type || 'other'}</div>
                                    </div>
                                    <div style={{ color: '#FF671F' }}>{item.waste_quantity}</div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>

                          {editingSubmissionId === submission.id ? (
                            <div className="mt-4 space-y-4">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {editSubmissionItems.map((item: any, idx: number) => {
                                  const accentColor = getItemAccentColor(item.product_type);
                                  return (
                                    <div key={`${submission.id}-edit-item-${idx}`} className="flex items-center justify-between rounded-2xl p-4" style={{ backgroundColor: '#FFFFFF' }}>
                                      <div>
                                        <div style={{ color: '#8B7355' }}>{item.product_name}</div>
                                        <div className="text-xs" style={{ color: '#8B7355' }}>{item.product_type || 'other'}</div>
                                      </div>
                                      <div className="flex items-center gap-3">
                                        <button
                                          onClick={() => adjustEditItemQuantity(idx, -1)}
                                          className="w-10 h-10 rounded-full text-white"
                                          style={{ backgroundColor: accentColor }}
                                        >
                                          -
                                        </button>
                                        <div className="min-w-[36px] text-center text-lg font-semibold" style={{ color: accentColor }}>
                                          {item.waste_quantity}
                                        </div>
                                        <button
                                          onClick={() => adjustEditItemQuantity(idx, 1)}
                                          className="w-10 h-10 rounded-full text-white"
                                          style={{ backgroundColor: accentColor }}
                                        >
                                          +
                                        </button>
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>

                              <div className="rounded-2xl p-4" style={{ backgroundColor: '#FFFFFF' }}>
                                <div className="text-sm mb-2" style={{ color: '#8B7355' }}>Add More from Directory</div>
                                <div className="flex flex-col gap-2 sm:flex-row">
                                  <select
                                    value={selectedAddProductId}
                                    onChange={(e) => setSelectedAddProductId(e.target.value)}
                                    className="flex-1 px-3 py-2 rounded-full border-2 focus:outline-none"
                                    style={{ borderColor: '#FFD7B5', color: '#8B7355', backgroundColor: '#FFFFFF' }}
                                  >
                                    <option value="">Select product...</option>
                                    {wasteDirectoryProducts.map((product: any) => (
                                      <option key={String(product.product_id)} value={String(product.product_id)}>
                                        {product.product_name} ({product.product_type || 'other'})
                                      </option>
                                    ))}
                                  </select>
                                  <button
                                    onClick={addDirectoryItemToEdit}
                                    className="px-4 py-2 rounded-full text-white transition-all hover:scale-105"
                                    style={{ backgroundColor: '#FF671F' }}
                                  >
                                    Add More
                                  </button>
                                </div>
                              </div>

                              <div>
                                <label className="text-sm" style={{ color: '#8B7355' }}>Notes</label>
                                <textarea
                                  value={editSubmissionNotes}
                                  onChange={(e) => setEditSubmissionNotes(e.target.value)}
                                  className="mt-2 w-full px-3 py-2 rounded-xl border-2 focus:outline-none"
                                  style={{ borderColor: '#FFD7B5', color: '#8B7355' }}
                                  rows={2}
                                />
                              </div>

                              <div className="flex flex-col gap-2 sm:flex-row">
                                <button
                                  onClick={() => saveEditSubmission(submission.id)}
                                  className="px-4 py-2 rounded-full text-white transition-all hover:scale-105"
                                  style={{ backgroundColor: '#FF671F' }}
                                >
                                  Save Edited Submission
                                </button>
                                <button
                                  onClick={cancelEditSubmission}
                                  className="px-4 py-2 rounded-full transition-all hover:scale-105"
                                  style={{ backgroundColor: '#E0D5C7', color: '#8B7355' }}
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          ) : (
                            <div className="mt-4 flex flex-col gap-2 sm:flex-row">
                              <button
                                onClick={() => handleApproveSubmission(submission.id)}
                                className="px-4 py-2 rounded-full text-white transition-all hover:scale-105"
                                style={{ backgroundColor: '#2F9E44' }}
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => startEditSubmission(submission)}
                                className="px-4 py-2 rounded-full text-white transition-all hover:scale-105"
                                style={{ backgroundColor: '#FF671F' }}
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => handleDiscardSubmission(submission.id)}
                                className="px-4 py-2 rounded-full text-white transition-all hover:scale-105"
                                style={{ backgroundColor: '#DA1884' }}
                              >
                                Discard
                              </button>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'predictions' && (
            <div className="bg-white rounded-3xl p-8 shadow-lg">
              <h3 className="mb-6" style={{ color: '#FF671F' }}>AI-Powered Forecast</h3>
              <p className="mb-8" style={{ color: '#8B7355' }}>
                Based on historical data, day of week, and recent trends, here's tomorrow's recommended production:
              </p>

              {forecastLoading ? (
                <div className="text-center py-8" style={{ color: '#8B7355' }}>Loading forecast...</div>
              ) : forecastPredictions.length === 0 ? (
                <div className="text-center py-8" style={{ color: '#8B7355' }}>
                  No forecast available. Click below to generate tomorrow's forecast.
                </div>
              ) : (
                <>
                  <div className="mb-8 space-y-6">
                    <div>
                      <h4 className="mb-3" style={{ color: '#DA1884' }}>Donuts</h4>
                      {donutForecasts.length === 0 ? (
                        <div className="p-4 rounded-2xl" style={{ backgroundColor: '#FFF8F0', color: '#8B7355' }}>
                          No donut forecast items.
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {donutForecasts.map((product: any) => (
                            <div key={`donut-${product.product_id}`} className="flex items-center justify-between p-4 rounded-2xl" style={{ backgroundColor: '#FFF8F0' }}>
                              <span style={{ color: '#8B7355' }}>{product.product_name}</span>
                              <span style={{ color: '#FF671F' }}>{getForecastQty(product)} units</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div>
                      <h4 className="mb-3" style={{ color: '#DA1884' }}>Munchkins</h4>
                      {munchkinForecasts.length === 0 ? (
                        <div className="p-4 rounded-2xl" style={{ backgroundColor: '#FFF8F0', color: '#8B7355' }}>
                          No munchkin forecast items.
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {munchkinForecasts.map((product: any) => (
                            <div key={`munchkin-${product.product_id}`} className="flex items-center justify-between p-4 rounded-2xl" style={{ backgroundColor: '#FFF8F0' }}>
                              <span style={{ color: '#8B7355' }}>{product.product_name}</span>
                              <span style={{ color: '#FF671F' }}>{getForecastQty(product)} units</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </>
              )}

              <button
                onClick={handleGenerateForecast}
                disabled={forecastLoading}
                className="w-full py-4 rounded-full text-white transition-all hover:scale-105 shadow-lg disabled:opacity-50"
                style={{ backgroundColor: '#FF671F' }}
              >
                {forecastLoading ? 'Generating...' : "Generate Tomorrow's Forecast"}
              </button>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="bg-white rounded-3xl p-8 shadow-lg">
              <h3 className="mb-6" style={{ color: '#FF671F' }}>Production History</h3>
              {historyLoading ? (
                <div style={{ color: '#8B7355' }}>Loading history...</div>
              ) : historyData.length === 0 ? (
                <div style={{ color: '#8B7355' }}>No historical data available yet</div>
              ) : (
                <div className="space-y-3">
                  {historyData.slice(0, 5).map((entry, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 rounded-2xl hover:shadow-md transition-all" style={{ backgroundColor: '#FFF8F0' }}>
                      <span style={{ color: '#8B7355' }}>{entry.date || `Day ${idx + 1}`}</span>
                      <div className="flex gap-6">
                        <span style={{ color: '#FF671F' }}>Production: {entry.production || '—'}</span>
                        <span style={{ color: '#DA1884' }}>Waste: {entry.waste ?? '—'} {entry.waste_pct != null ? `(${entry.waste_pct}%)` : ''}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'imported' && (
            <div className="bg-white rounded-3xl p-8 shadow-lg">
              <h3 className="mb-6" style={{ color: '#FF671F' }}>Imported Throwaway Data</h3>
              <p className="mb-6" style={{ color: '#8B7355' }}>
                View data imported from Excel files. Confirms your uploads were successful.
              </p>

              {importedDataLoading ? (
                <div style={{ color: '#8B7355' }}>Loading imported data...</div>
              ) : importedData.length === 0 ? (
                <div style={{ color: '#8B7355' }}>
                  <p>No imported data found in the last 30 days.</p>
                  <p className="text-sm mt-2">Use the Enter Daily Data tab to upload Excel files.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {importedData.map((week: any, idx: number) => (
                    <div key={idx} className="border rounded-lg p-4" style={{ borderColor: '#FFD7B5' }}>
                      <div className="mb-3">
                        <div>
                          <p className="font-semibold" style={{ color: '#FF671F' }}>
                            Week of {new Date(week.week_start).toLocaleDateString()} to {new Date(week.week_end).toLocaleDateString()}
                          </p>
                        </div>
                      </div>

                      {(() => {
                        const weekKey = `${week.week_start}-${week.week_end}-${idx}`;
                        const isExpanded = !!expandedImportedWeeks[weekKey];
                        return (
                          <>
                            <button
                              onClick={() => setExpandedImportedWeeks((prev) => ({ ...prev, [weekKey]: !isExpanded }))}
                              className="px-4 py-2 rounded-full text-white transition-all hover:scale-105"
                              style={{ backgroundColor: '#FF671F' }}
                            >
                              {isExpanded ? 'Hide' : 'View More'}
                            </button>

                            {isExpanded && (
                              <div className="border-t mt-3 pt-3" style={{ borderColor: '#FFD7B5' }}>
                                <div className="text-sm mb-3" style={{ color: '#8B7355' }}>
                                  {week.product_count} products, {week.total_records} records • Produced: {week.total_produced} • Waste: {week.total_waste}
                                </div>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 text-sm">
                                  {week.products.map((product: any, pidx: number) => (
                                    <div key={pidx} className="p-2 bg-gray-50 rounded">
                                      <p className="font-medium" style={{ color: '#2D1810' }}>
                                        {product.product_name}
                                      </p>
                                      <p style={{ color: '#8B7355' }} className="text-xs">
                                        {product.days_recorded} days: {product.produced || 0} produced, {product.waste || 0} waste
                                      </p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'qr-code' && (
            <div className="bg-white rounded-3xl p-8 shadow-lg">
              <h3 className="mb-6" style={{ color: '#FF671F' }}>QR Code Management</h3>
              <p className="mb-6" style={{ color: '#8B7355' }}>
                Generate and manage QR codes for waste submission. Staff can scan these codes to quickly log throwaway/waste data.
              </p>
              <ManagerQRCode storeId={storeId} />
            </div>
          )}
          </div>
        </div>
      </div>

      {/* Forecast Context Modal */}
      {showForecastModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
          onClick={() => setShowForecastModal(false)}
        >
          <div
            className="bg-white rounded-3xl p-8 shadow-2xl max-w-md w-full mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-2xl font-bold mb-6" style={{ color: '#FF671F' }}>
              Forecast Context
            </h3>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: '#8B7355' }}>
                  Expected Business Level
                </label>
                <select
                  value={forecastBusinessLevel}
                  onChange={(e) => setForecastBusinessLevel(e.target.value as 'normal' | 'busy' | 'slower')}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-[#FF671F] focus:outline-none"
                >
                  <option value="normal">Normal</option>
                  <option value="busy">Busy (+20%)</option>
                  <option value="slower">Slower (-20%)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: '#8B7355' }}>
                  Reason / Event
                </label>
                <select
                  value={forecastReason}
                  onChange={(e) => setForecastReason(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-[#FF671F] focus:outline-none"
                >
                  <option value="regular_day">Regular Day</option>
                  <option value="school">School Event</option>
                  <option value="weather">Weather Related</option>
                  <option value="holiday">Holiday</option>
                  <option value="special_occasion">Special Occasion</option>
                  <option value="promotion">Promotion</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: '#8B7355' }}>
                  Additional Notes (Optional)
                </label>
                <textarea
                  value={forecastNotes}
                  onChange={(e) => setForecastNotes(e.target.value)}
                  placeholder="Any specific details..."
                  rows={3}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-[#FF671F] focus:outline-none resize-none"
                />
              </div>

              <div className="flex gap-3 mt-8">
                <button
                  onClick={() => setShowForecastModal(false)}
                  className="flex-1 py-3 rounded-full border-2 transition-all hover:bg-gray-50"
                  style={{ borderColor: '#8B7355', color: '#8B7355' }}
                >
                  Cancel
                </button>
                <button
                  onClick={submitForecastGeneration}
                  className="flex-1 py-3 rounded-full text-white transition-all hover:scale-105 shadow-lg"
                  style={{ backgroundColor: '#FF671F' }}
                >
                  Generate Forecast
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
