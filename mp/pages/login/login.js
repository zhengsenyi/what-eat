// pages/login/login.js
const { userApi } = require('../../utils/api');

Page({
  data: {
    isLoading: false,
    isRegisterMode: false,
    username: '',
    password: '',
    confirmPassword: ''
  },

  onLoad() {
    // 检查是否已登录
    const token = wx.getStorageSync('token');
    console.log('检查登录状态，token:', token ? '存在' : '不存在');
    if (token) {
      console.log('已登录，跳转到首页');
      wx.reLaunch({
        url: '/pages/index/index',
        success: () => {
          console.log('自动跳转成功');
        },
        fail: (err) => {
          console.error('自动跳转失败:', err);
        }
      });
    }
  },

  // 切换登录/注册模式
  toggleMode() {
    this.setData({
      isRegisterMode: !this.data.isRegisterMode,
      username: '',
      password: '',
      confirmPassword: ''
    });
  },

  // 输入用户名
  onUsernameInput(e) {
    this.setData({ username: e.detail.value });
  },

  // 输入密码
  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  // 输入确认密码
  onConfirmPasswordInput(e) {
    this.setData({ confirmPassword: e.detail.value });
  },

  // 登录
  async onLogin() {
    if (this.data.isLoading) return;

    const { username, password } = this.data;

    // 验证输入
    if (!username || username.length < 3) {
      wx.showToast({ title: '用户名至少3个字符', icon: 'none' });
      return;
    }
    if (!password || password.length < 6) {
      wx.showToast({ title: '密码至少6个字符', icon: 'none' });
      return;
    }

    this.setData({ isLoading: true });
    wx.showLoading({ title: '登录中...', mask: true });

    try {
      console.log('开始登录请求...');
      const res = await userApi.login(username, password);
      console.log('登录响应:', res);
      
      // 检查响应格式：后端返回 {code: 0, msg: "登录成功", data: {access_token: "..."}}
      if (!res || res.code !== 0 || !res.data || !res.data.access_token) {
        throw new Error(res?.msg || '登录响应无效');
      }
      
      // 保存token
      wx.setStorageSync('token', res.data.access_token);
      console.log('Token已保存:', res.data.access_token);
      
      // 获取用户信息
      try {
        const userInfoRes = await userApi.getUserInfo();
        console.log('用户信息响应:', userInfoRes);
        // 后端返回格式：{code: 0, data: {id, username, created_at, today_remaining_times}}
        if (userInfoRes && userInfoRes.code === 0 && userInfoRes.data) {
          const userInfo = userInfoRes.data;
          wx.setStorageSync('userInfo', {
            id: userInfo.id,
            username: userInfo.username,
            nickName: userInfo.username,
            avatarText: '👤',
            level: '黄金会员',
            remainingTimes: userInfo.today_remaining_times,
            createdAt: userInfo.created_at
          });
        }
      } catch (e) {
        console.error('获取用户信息失败', e);
      }

      wx.hideLoading();
      this.setData({ isLoading: false });
      
      wx.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 1000,
        success: () => {
          console.log('Toast显示成功，准备跳转...');
        }
      });

      // 直接跳转，不等待Toast完成
      setTimeout(() => {
        console.log('执行页面跳转...');
        wx.reLaunch({
          url: '/pages/index/index',
          success: () => {
            console.log('跳转成功');
          },
          fail: (err) => {
            console.error('跳转失败:', err);
            // 尝试使用switchTab
            wx.switchTab({
              url: '/pages/index/index',
              fail: (err2) => {
                console.error('switchTab也失败:', err2);
                // 最后尝试redirectTo
                wx.redirectTo({
                  url: '/pages/index/index',
                  fail: (err3) => {
                    console.error('redirectTo也失败:', err3);
                  }
                });
              }
            });
          }
        });
      }, 1000);

    } catch (err) {
      wx.hideLoading();
      this.setData({ isLoading: false });
      console.error('登录失败', err);
      
      let errorMsg = '登录失败，请检查用户名和密码';
      if (err && err.detail) {
        errorMsg = err.detail;
      } else if (err && err.message) {
        errorMsg = err.message;
      }
      
      wx.showToast({
        title: errorMsg,
        icon: 'none'
      });
    }
  },

  // 注册
  async onRegister() {
    if (this.data.isLoading) return;

    const { username, password, confirmPassword } = this.data;

    // 验证输入
    if (!username || username.length < 3) {
      wx.showToast({ title: '用户名至少3个字符', icon: 'none' });
      return;
    }
    if (!password || password.length < 6) {
      wx.showToast({ title: '密码至少6个字符', icon: 'none' });
      return;
    }
    if (password !== confirmPassword) {
      wx.showToast({ title: '两次密码输入不一致', icon: 'none' });
      return;
    }

    this.setData({ isLoading: true });
    wx.showLoading({ title: '注册中...', mask: true });

    try {
      console.log('开始注册请求...');
      await userApi.register(username, password);
      console.log('注册成功');
      
      wx.hideLoading();
      this.setData({ isLoading: false });
      
      wx.showToast({ title: '注册成功，请登录', icon: 'success', duration: 1500 });

      setTimeout(() => {
        this.setData({
          isRegisterMode: false,
          confirmPassword: ''
        });
      }, 1500);

    } catch (err) {
      wx.hideLoading();
      this.setData({ isLoading: false });
      console.error('注册失败', err);
      
      let errorMsg = '注册失败，用户名可能已存在';
      if (err && err.detail) {
        errorMsg = err.detail;
      } else if (err && err.message) {
        errorMsg = err.message;
      }
      
      wx.showToast({
        title: errorMsg,
        icon: 'none'
      });
    }
  },

  // 跳转到首页
  navigateToIndex() {
    console.log('navigateToIndex被调用');
    wx.reLaunch({
      url: '/pages/index/index',
      success: () => {
        console.log('reLaunch成功');
      },
      fail: (err) => {
        console.error('reLaunch失败:', err);
      }
    });
  },

  // 查看用户协议
  onViewAgreement() {
    wx.showModal({
      title: '用户协议',
      content: '这里是用户协议的详细内容...',
      showCancel: false,
      confirmText: '我知道了'
    });
  },

  // 查看隐私政策
  onViewPrivacy() {
    wx.showModal({
      title: '隐私政策',
      content: '这里是隐私政策的详细内容...',
      showCancel: false,
      confirmText: '我知道了'
    });
  }
});
