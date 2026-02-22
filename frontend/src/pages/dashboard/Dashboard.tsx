import React, { useState, useEffect } from 'react';

/// <reference types="vite/client" />
import { LayoutDashboard, Pencil, TrendingUp, History, Menu, X, Plus, Trash2, Edit2, Download, QrCode } from 'lucide-react';
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
  const [sidebarOpen, setSidebarOpen] = useState(true);
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
  const [importHistoryData, setImportHistoryData] = useState<any[]>([]);
  const [importHistoryLoading, setImportHistoryLoading] = useState(true);
  const [wasteTrendData, setWasteTrendData] = useState<any[]>([]);
  const [wasteTrendLoading, setWasteTrendLoading] = useState(true);

  const [quantities, setQuantities] = useState<Record<string, number>>(
    [...donutTypes, ...munchkinTypes].reduce((acc, item) => ({ ...acc, [item]: 0 }), {})
  );

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
      setQuickStatsData(result.stats_7d || {});
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
      const result = await apiFetch(`/dashboard/production-summary?store_id=${storeId}&days=28`);
      
      if (result.daily_data && result.daily_data.length > 0) {
        // Transform for line chart - show weekly averages
        const weeklyGroups: any = {};
        result.daily_data.forEach((item: any, idx: number) => {
          const weekNum = Math.ceil((result.daily_data.length - idx) / 7);
          if (!weeklyGroups[weekNum]) {
            weeklyGroups[weekNum] = { week: `Week ${weekNum}`, production: 0, optimal: 0, count: 0 };
          }
          weeklyGroups[weekNum].production += item.total_quantity || 0;
          weeklyGroups[weekNum].count += 1;
        });
        
        // Calculate averages and optimal (20% less than actual)
        const transformedData = Object.values(weeklyGroups).map((w: any) => ({
          week: w.week,
          production: Math.round(w.production / w.count),
          optimal: Math.round((w.production / w.count) * 0.8)
        }));
        
        setProductionTrendData(transformedData.slice(0, 4));
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

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setHistoryLoading(true);
        const result = await apiFetch(`/forecast_history/?store_id=${storeId}&days=7`);
        setHistoryData(result || []);
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
  }, []);

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
    { week: 'Week 1', production: 0, optimal: 0 },
    { week: 'Week 2', production: 0, optimal: 0 },
    { week: 'Week 3', production: 0, optimal: 0 },
    { week: 'Week 4', production: 0, optimal: 0 }
  ];

  const navItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'data-entry', icon: Pencil, label: 'Enter Daily Data' },
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
      // Get current week's Sunday
      const today = new Date();
      const dayOfWeek = today.getDay();
      const daysToSunday = dayOfWeek === 0 ? 0 : dayOfWeek;
      const sunday = new Date(today);
      sunday.setDate(today.getDate() - daysToSunday);
      const weekStart = sunday.toISOString().split('T')[0];

      // Call backend export endpoint
      const baseUrl = import.meta.env.VITE_API_URL || 'https://dunkin-demand-intelligence-landing-page.onrender.com/api/v1';
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
    setForecastLoading(true);
    try {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const targetDate = tomorrow.toISOString().split("T")[0];
      
      const result = await apiFetch("/forecast/raw", {
        method: "POST",
        body: JSON.stringify({
          store_id: storeId,
          target_date: targetDate
        })
      });
      
      alert("Forecast generated successfully!");
      console.log("Forecast result:", result);
      
      // Fetch the generated forecast to display
      await fetchForecastPredictions(targetDate);
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
      }
    } catch (err) {
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
    <div className="flex h-screen" style={{ backgroundColor: '#F5F0E8' }}>
      {/* Sidebar */}
      <aside
        className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 overflow-hidden flex-shrink-0`}
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

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {/* Top Bar */}
        <div className="bg-white shadow-sm p-4 flex items-center justify-between sticky top-0 z-10">
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
            className="flex items-center gap-2 px-4 py-2 rounded-full text-white transition-all hover:scale-105"
            style={{ backgroundColor: '#FF671F' }}
          >
            <Download size={18} />
            Export Data
          </button>
        </div>

        {/* Dashboard Content */}
        <div className="p-6">
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Greeting */}
              <div className="bg-gradient-to-r from-orange-50 to-pink-50 rounded-3xl p-6 shadow-lg">
                <h2 style={{ color: '#FF671F' }}>Hey {username}! 👋</h2>
                <p style={{ color: '#8B7355' }}>Welcome back to your Dunkin' Demand Intelligence dashboard.</p>
              </div>

              {/* Quick Stats */}
              <div className="grid md:grid-cols-4 gap-6">
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
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-white rounded-3xl p-6 shadow-lg">
                  <h3 className="mb-4" style={{ color: '#FF671F' }}>Weekly Waste vs Sales</h3>
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
                        <XAxis dataKey="week" stroke="#8B7355" />
                        <YAxis stroke="#8B7355" />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="production" stroke="#DA1884" strokeWidth={3} />
                        <Line type="monotone" dataKey="optimal" stroke="#FF671F" strokeWidth={3} />
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

                  <div className="grid md:grid-cols-2 gap-4">
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

                  <div className="grid md:grid-cols-2 gap-4">
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
                  {/* All Products */}
                  <div className="mb-8">
                    <h4 className="mb-4" style={{ color: '#DA1884' }}>All Products</h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      {forecastPredictions.map((product) => (
                        <div key={product.product_id} className="flex items-center justify-between p-4 rounded-2xl" style={{ backgroundColor: '#FFF8F0' }}>
                          <span style={{ color: '#8B7355' }}>{product.product_name}</span>
                          <span style={{ color: '#FF671F' }}>{product.final_quantity || product.predicted_quantity || 0} units</span>
                        </div>
                      ))}
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
                        <span style={{ color: '#DA1884' }}>Waste: {entry.waste_pct ? entry.waste_pct + '%' : '—'}</span>
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
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <p className="font-semibold" style={{ color: '#FF671F' }}>
                            Week of {new Date(week.week_start).toLocaleDateString()} to {new Date(week.week_end).toLocaleDateString()}
                          </p>
                          <p className="text-sm" style={{ color: '#8B7355' }}>
                            {week.product_count} products, {week.total_records} records
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm" style={{ color: '#8B7355' }}>
                            Produced: <span className="font-semibold">{week.total_produced}</span>
                          </p>
                          <p className="text-sm" style={{ color: '#8B7355' }}>
                            Waste: <span className="font-semibold">{week.total_waste}</span>
                          </p>
                        </div>
                      </div>

                      <div className="border-t" style={{ borderColor: '#FFD7B5' }}>
                        <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 text-sm">
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
  );
}
