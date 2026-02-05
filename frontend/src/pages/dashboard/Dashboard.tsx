import React, { useState, useEffect } from 'react';

import { LayoutDashboard, Pencil, TrendingUp, History, Menu, X, Plus, Trash2, Edit2, Download } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { apiClient } from '../../api/client';

interface DashboardProps {
  onLogout: () => void;
  username: string;
  donutTypes: string[];
  munchkinTypes: string[];
  onUpdateDonutTypes: (types: string[]) => void;
  onUpdateMunchkinTypes: (types: string[]) => void;
}

export function Dashboard({ onLogout, username, donutTypes, munchkinTypes, onUpdateDonutTypes, onUpdateMunchkinTypes }: DashboardProps) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [editingItem, setEditingItem] = useState<{ type: 'donut' | 'munchkin'; index: number; value: string } | null>(null);
  const [newItemName, setNewItemName] = useState('');
  const [addingType, setAddingType] = useState<'donut' | 'munchkin' | null>(null);

  const [quantities, setQuantities] = useState<Record<string, number>>(
    [...donutTypes, ...munchkinTypes].reduce((acc, item) => ({ ...acc, [item]: 0 }), {})
  );

  const [daily, setDaily] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError('');
        
        // Fetch forecast data from API
        const forecastData = await apiClient.getForecast(1, new Date().toISOString().split('T')[0]);
        setForecast(forecastData);

        // Fetch other dashboard data if needed
        setDaily({ status: 'ok' });
      } catch (err: any) {
        setError(err.message || 'Failed to fetch dashboard data');
        console.error('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const wasteData = [
    { day: 'Mon', waste: 12, sales: 88 },
    { day: 'Tue', waste: 8, sales: 92 },
    { day: 'Wed', waste: 15, sales: 85 },
    { day: 'Thu', waste: 6, sales: 94 },
    { day: 'Fri', waste: 10, sales: 90 },
    { day: 'Sat', waste: 5, sales: 95 },
    { day: 'Sun', waste: 7, sales: 93 }
  ];

  const trendData = [
    { week: 'Week 1', production: 650, optimal: 620 },
    { week: 'Week 2', production: 640, optimal: 625 },
    { week: 'Week 3', production: 620, optimal: 615 },
    { week: 'Week 4', production: 625, optimal: 620 }
  ];

  const navItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'data-entry', icon: Pencil, label: 'Enter Daily Data' },
    { id: 'predictions', icon: TrendingUp, label: 'Predictions' },
    { id: 'history', icon: History, label: 'History' }
  ];

  const handleAddItem = (type: 'donut' | 'munchkin') => {
    if (!newItemName.trim()) return;

    if (type === 'donut') {
      onUpdateDonutTypes([...donutTypes, newItemName]);
    } else {
      onUpdateMunchkinTypes([...munchkinTypes, newItemName]);
    }

    setQuantities({ ...quantities, [newItemName]: 0 });
    setNewItemName('');
    setAddingType(null);
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

  const handleExportData = () => {
    const data = {
      store: 'Store #12345',
      date: new Date().toLocaleDateString(),
      quantities,
      donutTypes,
      munchkinTypes,
      wasteData,
      trendData
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dunkin-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return
  
  async function handleSaveData() {
  const items = Object.keys(quantities).map((key) => ({
    name: key,
    produced: quantities[key],
    waste: Math.max(0, Math.floor(quantities[key] * 0.08))  // default 8% waste for now
  }));

  await apiFetch("/dashboard/daily", {
    method: "POST",
    body: JSON.stringify({
      date: new Date().toISOString().split("T")[0],
      items: items
    })
  });
  });

  alert("Saved Successfully!");
}
(
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
              <div style={{ color: '#FF671F' }}>Store #12345</div>
              <div className="text-sm" style={{ color: '#8B7355' }}>Thursday, November 27, 2025</div>
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
                <p style={{ color: '#8B7355' }}>Welcome back to your Dunkin\u2019 Demand Intelligence dashboard.</p>
              </div>

              {/* Quick Stats */}
              <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-white rounded-3xl p-6 shadow-lg">
                  <div className="text-sm mb-2" style={{ color: '#8B7355' }}>Today's Production</div>
                  <div className="text-3xl" style={{ color: '#FF671F' }}>842 Units</div>
                </div>
                <div className="bg-white rounded-3xl p-6 shadow-lg">
                  <div className="text-sm mb-2" style={{ color: '#8B7355' }}>Predicted Waste</div>
                  <div className="text-3xl" style={{ color: '#DA1884' }}>5.2%</div>
                </div>
                <div className="bg-white rounded-3xl p-6 shadow-lg">
                  <div className="text-sm mb-2" style={{ color: '#8B7355' }}>Tomorrow's Forecast</div>
                  <div className="text-3xl" style={{ color: '#FF671F' }}>798 Units</div>
                </div>
              </div>

              {/* Charts */}
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-white rounded-3xl p-6 shadow-lg">
                  <h3 className="mb-4" style={{ color: '#FF671F' }}>Weekly Waste vs Sales</h3>
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
                </div>

                <div className="bg-white rounded-3xl p-6 shadow-lg">
                  <h3 className="mb-4" style={{ color: '#FF671F' }}>Production Optimization</h3>
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
                </div>
              </div>
            </div>
          )}

          {activeTab === 'data-entry' && (
            <div className="space-y-6">
              <div className="bg-white rounded-3xl p-8 shadow-lg">
                <h3 className="mb-6" style={{ color: '#FF671F' }}>Daily Donut & Munchkin Input</h3>

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
                  className="w-full mt-8 py-4 rounded-full text-white"
                  style={{ backgroundColor: '#FF671F' }}
                >
                  Save Today's Data
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

              {/* Donuts Predictions */}
              <div className="mb-8">
                <h4 className="mb-4" style={{ color: '#DA1884' }}>Donuts</h4>
                <div className="grid md:grid-cols-2 gap-4">
                  {donutTypes.map((donut, idx) => (
                    <div key={donut} className="flex items-center justify-between p-4 rounded-2xl" style={{ backgroundColor: '#FFF8F0' }}>
                      <span style={{ color: '#8B7355' }}>{donut}</span>
                      <span style={{ color: '#FF671F' }}>{Math.floor(Math.random() * 30) + 30} units</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Munchkins Predictions */}
              <div className="mb-8">
                <h4 className="mb-4" style={{ color: '#DA1884' }}>Munchkins</h4>
                <div className="grid md:grid-cols-2 gap-4">
                  {munchkinTypes.map((munchkin, idx) => (
                    <div key={munchkin} className="flex items-center justify-between p-4 rounded-2xl" style={{ backgroundColor: '#FFF8F0' }}>
                      <span style={{ color: '#8B7355' }}>{munchkin}</span>
                      <span style={{ color: '#DA1884' }}>{Math.floor(Math.random() * 50) + 100} units</span>
                    </div>
                  ))}
                </div>
              </div>

              <button
                className="w-full py-4 rounded-full text-white transition-all hover:scale-105 shadow-lg"
                style={{ backgroundColor: '#FF671F' }}
              >
                Generate Tomorrow's Forecast
              </button>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="bg-white rounded-3xl p-8 shadow-lg">
              <h3 className="mb-6" style={{ color: '#FF671F' }}>Production History</h3>
              <div className="space-y-3">
                {['Nov 26, 2025', 'Nov 25, 2025', 'Nov 24, 2025', 'Nov 23, 2025', 'Nov 22, 2025'].map((date, idx) => (
                  <div key={date} className="flex items-center justify-between p-4 rounded-2xl hover:shadow-md transition-all" style={{ backgroundColor: '#FFF8F0' }}>
                    <span style={{ color: '#8B7355' }}>{date}</span>
                    <div className="flex gap-6">
                      <span style={{ color: '#FF671F' }}>Production: {850 - idx * 15}</span>
                      <span style={{ color: '#DA1884' }}>Waste: {8 - idx}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
