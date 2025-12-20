// pages/profile/profile.js
const { userApi } = require('../../utils/api');

Page({
  data: {
    // 导航栏相关
    statusBarHeight: 20,
    navBarHeight: 44,
    menuButtonWidth: 87,
    // 用户信息
    userInfo: {
      id: 0,
      username: '',
      nickName: '美食探索家',
      avatarText: '👤',
      level: '黄金会员',
      remainingTimes: 3
    },
    version: '1.0.0',
    cacheSize: '计算中...'
  },

  onLoad() {
    // 获取导航栏信息
    this.getNavBarInfo();
    this.loadUserInfo();
    this.calculateCacheSize();
  },

  onShow() {
    // 每次显示页面时刷新数据
    this.loadUserInfo();
    this.calculateCacheSize();
  },

  // 获取导航栏信息
  getNavBarInfo() {
    try {
      const systemInfo = wx.getSystemInfoSync();
      const statusBarHeight = systemInfo.statusBarHeight || 20;
      const menuButtonInfo = wx.getMenuButtonBoundingClientRect();
      const navBarHeight = (menuButtonInfo.top - statusBarHeight) * 2 + menuButtonInfo.height;
      const menuButtonWidth = systemInfo.windowWidth - menuButtonInfo.left;
      
      this.setData({
        statusBarHeight,
        navBarHeight,
        menuButtonWidth
      });
    } catch (e) {
      console.error('获取导航栏信息失败', e);
    }
  },

  // 加载用户信息
  async loadUserInfo() {
    try {
      const res = await userApi.getUserInfo();
      
      // 后端返回格式：{code: 0, data: {id, username, created_at, today_remaining_times}}
      if (res && res.code === 0 && res.data) {
        const userInfo = res.data;
        const localUserInfo = wx.getStorageSync('userInfo') || {};
        
        this.setData({
          userInfo: {
            id: userInfo.id,
            username: userInfo.username,
            nickName: localUserInfo.nickName || userInfo.username,
            avatarText: localUserInfo.avatarText || '👤',
            level: '黄金会员',
            remainingTimes: userInfo.today_remaining_times
          }
        });

        // 更新本地存储
        wx.setStorageSync('userInfo', {
          ...localUserInfo,
          id: userInfo.id,
          username: userInfo.username,
          remainingTimes: userInfo.today_remaining_times
        });
      }
    } catch (e) {
      console.error('获取用户信息失败', e);
      // 使用本地存储的信息
      const localUserInfo = wx.getStorageSync('userInfo');
      if (localUserInfo) {
        this.setData({
          userInfo: {
            id: localUserInfo.id || 0,
            username: localUserInfo.username || '',
            nickName: localUserInfo.nickName || '美食探索家',
            avatarText: localUserInfo.avatarText || '👤',
            level: '黄金会员',
            remainingTimes: localUserInfo.remainingTimes || 0
          }
        });
      }
    }
  },

  // 计算缓存大小
  calculateCacheSize() {
    try {
      const res = wx.getStorageInfoSync();
      const usedSize = res.currentSize;
      let sizeText = '';
      
      if (usedSize < 1024) {
        sizeText = `${usedSize} KB`;
      } else {
        sizeText = `${(usedSize / 1024).toFixed(2)} MB`;
      }
      
      this.setData({ cacheSize: sizeText });
    } catch (e) {
      this.setData({ cacheSize: '未知' });
    }
  },

  // 编辑个人资料
  editProfile() {
    wx.showActionSheet({
      itemList: ['修改昵称', '修改头像'],
      success: (res) => {
        if (res.tapIndex === 0) {
          this.editNickname();
        } else if (res.tapIndex === 1) {
          this.editAvatar();
        }
      }
    });
  },

  // 修改昵称
  editNickname() {
    wx.showModal({
      title: '修改昵称',
      editable: true,
      placeholderText: '请输入新昵称',
      success: (res) => {
        if (res.confirm && res.content) {
          const userInfo = wx.getStorageSync('userInfo') || {};
          userInfo.nickName = res.content;
          wx.setStorageSync('userInfo', userInfo);
          
          this.setData({
            'userInfo.nickName': res.content
          });
          
          wx.showToast({
            title: '修改成功',
            icon: 'success'
          });
        }
      }
    });
  },

  // 修改头像
  editAvatar() {
    const avatars = ['👤', '😊', '🤗', '😎', '🥳', '🤩', '😋', '🍜'];
    wx.showActionSheet({
      itemList: avatars,
      success: (res) => {
        const userInfo = wx.getStorageSync('userInfo') || {};
        userInfo.avatarText = avatars[res.tapIndex];
        wx.setStorageSync('userInfo', userInfo);
        
        this.setData({
          'userInfo.avatarText': avatars[res.tapIndex]
        });
        
        wx.showToast({
          title: '修改成功',
          icon: 'success'
        });
      }
    });
  },

  // 跳转到历史页
  goToHistory() {
    wx.navigateTo({
      url: '/pages/history/history'
    });
  },

  // 跳转到意见反馈
  goToFeedback() {
    wx.showModal({
      title: '意见反馈',
      content: '如有问题或建议，请联系我们：\nfeedback@chisha.com',
      showCancel: false,
      confirmText: '知道了'
    });
  },

  // 跳转到关于我们
  goToAbout() {
    wx.showModal({
      title: '关于吃啥盲盒',
      content: '版本：1.0.0\n\n吃啥盲盒是一款帮助你解决"今天吃什么"难题的小程序。\n\n让美食选择变得有趣又简单！',
      showCancel: false,
      confirmText: '知道了'
    });
  },

  // 清除缓存
  clearCache() {
    wx.showModal({
      title: '清除缓存',
      content: '确定要清除所有缓存数据吗？这将清除本地历史记录，但不会影响登录状态。',
      confirmText: '确定清除',
      confirmColor: '#ef4444',
      success: (res) => {
        if (res.confirm) {
          const token = wx.getStorageSync('token');
          const userInfo = wx.getStorageSync('userInfo');
          
          wx.clearStorageSync();
          
          if (token) {
            wx.setStorageSync('token', token);
          }
          if (userInfo) {
            wx.setStorageSync('userInfo', userInfo);
          }
          
          this.calculateCacheSize();
          
          wx.showToast({
            title: '清除成功',
            icon: 'success'
          });
        }
      }
    });
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      confirmText: '退出',
      confirmColor: '#ef4444',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          
          wx.showToast({
            title: '已退出登录',
            icon: 'none',
            duration: 1500
          });
          
          setTimeout(() => {
            wx.reLaunch({
              url: '/pages/login/login'
            });
          }, 1500);
        }
      }
    });
  },

  // 分享
  onShareAppMessage() {
    return {
      title: '吃啥盲盒 - 解决你的选择困难症！',
      path: '/pages/login/login'
    };
  }
});
