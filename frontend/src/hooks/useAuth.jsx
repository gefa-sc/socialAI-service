/**
 * SocialAI Service - 认证状态管理
 */
import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, storage } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 初始化时检查登录状态
  useEffect(() => {
    const initAuth = async () => {
      const token = storage.getToken();
      if (token) {
        try {
          const response = await authAPI.getCurrentUser();
          setUser(response.data);
        } catch (error) {
          // Token无效，清除存储
          storage.clear();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  // 登录
  const login = async (email, password) => {
    const response = await authAPI.login(email, password);
    const { access_token } = response.data;
    storage.setToken(access_token);
    
    // 获取用户信息
    const userResponse = await authAPI.getCurrentUser();
    setUser(userResponse.data);
    storage.setUser(userResponse.data);
    
    return userResponse.data;
  };

  // 注册
  const register = async (data) => {
    const response = await authAPI.register(data);
    // 注册后自动登录
    return login(data.email, data.password);
  };

  // 退出
  const logout = () => {
    authAPI.logout();
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// 使用认证状态的Hook
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth必须在AuthProvider内使用');
  }
  return context;
}

export default AuthContext;
