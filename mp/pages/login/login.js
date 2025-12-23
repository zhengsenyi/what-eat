// pages/login/login.js
const { userApi, BASE_URL } = require('../../utils/api');

// 处理头像URL，如果是相对路径则拼接服务器地址
function getFullAvatarUrl(avatarUrl) {
  if (!avatarUrl) return '';
  if (avatarUrl.startsWith('http://') || avatarUrl.startsWith('https://') || avatarUrl.startsWith('wxfile://')) {
    return avatarUrl;
  }
  // 相对路径，拼接服务器地址
  return BASE_URL + avatarUrl;
}

Page({
  data: {
    isLoading: false,
    isWechatLoading: false,
    isRegisterMode: false,
    username: '',
    password: '',
    confirmPassword: '',
    // 微信用户信息授权相关
    showUserInfoModal: false,
    tempAvatarUrl: '',
    tempNickname: ''
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

  // 微信授权登录
  async onWechatLogin() {
    if (this.data.isWechatLoading) return;

    this.setData({ isWechatLoading: true });
    wx.showLoading({ title: '微信登录中...', mask: true });

    try {
      // 1. 调用 wx.login 获取 code
      const loginRes = await new Promise((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject
        });
      });

      if (!loginRes.code) {
        throw new Error('获取微信登录凭证失败');
      }

      console.log('获取到微信code:', loginRes.code);

      // 2. 调用后端接口进行微信登录
      const res = await userApi.wechatLogin(loginRes.code);
      console.log('微信登录响应:', res);

      // 检查响应格式
      if (!res || res.code !== 0 || !res.data || !res.data.access_token) {
        throw new Error(res?.msg || '微信登录响应无效');
      }

      // 3. 保存token
      wx.setStorageSync('token', res.data.access_token);
      console.log('Token已保存:', res.data.access_token);

      // 4. 保存用户信息
      const userData = res.data.user;
      const isNewUser = res.data.is_new_user;
      
      wx.setStorageSync('userInfo', {
        id: userData.id,
        openid: userData.openid,
        nickName: userData.nickname || '微信用户',
        avatarUrl: userData.avatar_url || '',  // 存储原始URL
        avatarText: '👤',
        level: '黄金会员',
        isWechatUser: true,
        createdAt: userData.created_at
      });

      // 5. 获取完整用户信息（包含剩余次数等）
      try {
        const userInfoRes = await userApi.getUserInfo();
        console.log('用户信息响应:', userInfoRes);
        if (userInfoRes && userInfoRes.code === 0 && userInfoRes.data) {
          const userInfo = userInfoRes.data;
          wx.setStorageSync('userInfo', {
            id: userInfo.id,
            openid: userInfo.openid,
            username: userInfo.username,
            nickName: userInfo.nickname || userInfo.username || '微信用户',
            avatarUrl: userInfo.avatar_url || '',  // 存储原始URL
            avatarText: '👤',
            level: '黄金会员',
            remainingTimes: userInfo.today_remaining_times,
            isWechatUser: !!userInfo.openid,
            createdAt: userInfo.created_at
          });
        }
      } catch (e) {
        console.error('获取用户信息失败', e);
      }

      wx.hideLoading();
      this.setData({ isWechatLoading: false });

      // 如果是新用户且没有昵称和头像，显示授权弹窗
      if (isNewUser && (!userData.nickname || !userData.avatar_url)) {
        this.setData({
          showUserInfoModal: true,
          tempAvatarUrl: '',
          tempNickname: ''
        });
      } else {
        wx.showToast({
          title: isNewUser ? '注册成功' : '登录成功',
          icon: 'success',
          duration: 1000
        });

        // 跳转到首页
        this.navigateToIndex();
      }

    } catch (err) {
      wx.hideLoading();
      this.setData({ isWechatLoading: false });
      console.error('微信登录失败', err);

      let errorMsg = '微信登录失败，请稍后重试';
      if (err && err.msg) {
        errorMsg = err.msg;
      } else if (err && err.message) {
        errorMsg = err.message;
      }

      wx.showToast({
        title: errorMsg,
        icon: 'none'
      });
    }
  },

  // 选择头像回调
  async onChooseAvatar(e) {
    const { avatarUrl } = e.detail;
    console.log('选择的头像临时路径:', avatarUrl);
    
    // 先显示临时头像
    this.setData({
      tempAvatarUrl: avatarUrl
    });

    // 上传头像到服务器
    wx.showLoading({ title: '上传中...', mask: true });
    try {
      const res = await userApi.uploadAvatar(avatarUrl);
      console.log('头像上传响应:', res);
      
      if (res && res.code === 0 && res.data && res.data.avatar_url) {
        // 使用服务器返回的URL
        const serverAvatarUrl = res.data.avatar_url;
        this.setData({
          tempAvatarUrl: serverAvatarUrl
        });
        console.log('头像上传成功，服务器URL:', serverAvatarUrl);
      } else {
        console.error('头像上传失败:', res);
        wx.showToast({
          title: res?.msg || '头像上传失败',
          icon: 'none'
        });
      }
    } catch (err) {
      console.error('头像上传异常:', err);
      wx.showToast({
        title: '头像上传失败',
        icon: 'none'
      });
    } finally {
      wx.hideLoading();
    }
  },

  // 输入昵称回调
  onNicknameInput(e) {
    const nickname = e.detail.value;
    console.log('输入的昵称:', nickname);
    this.setData({
      tempNickname: nickname
    });
  },

  // 确认用户信息
  async onConfirmUserInfo() {
    const { tempAvatarUrl, tempNickname } = this.data;
    
    if (!tempAvatarUrl && !tempNickname) {
      wx.showToast({
        title: '请选择头像或填写昵称',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({ title: '保存中...', mask: true });

    try {
      // 如果头像是临时文件路径（以 http://tmp 或 wxfile:// 开头），需要先上传
      let finalAvatarUrl = tempAvatarUrl;
      if (tempAvatarUrl && (tempAvatarUrl.startsWith('http://tmp') || tempAvatarUrl.startsWith('wxfile://'))) {
        console.log('检测到临时头像路径，开始上传...');
        const uploadRes = await userApi.uploadAvatar(tempAvatarUrl);
        if (uploadRes && uploadRes.code === 0 && uploadRes.data && uploadRes.data.avatar_url) {
          finalAvatarUrl = uploadRes.data.avatar_url;
          console.log('头像上传成功:', finalAvatarUrl);
        } else {
          throw new Error(uploadRes?.msg || '头像上传失败');
        }
      }

      // 调用后端接口更新用户信息（昵称）
      // 头像已经在上传时更新了，这里只需要更新昵称
      if (tempNickname) {
        const res = await userApi.updateWechatUserInfo(tempNickname, null);
        console.log('更新昵称响应:', res);
        if (res && res.code !== 0) {
          throw new Error(res?.msg || '保存昵称失败');
        }
      }

      // 更新本地存储（存储原始URL）
      const userInfo = wx.getStorageSync('userInfo') || {};
      if (tempNickname) {
        userInfo.nickName = tempNickname;
      }
      if (finalAvatarUrl) {
        userInfo.avatarUrl = finalAvatarUrl;
      }
      wx.setStorageSync('userInfo', userInfo);

      wx.hideLoading();
      this.setData({ showUserInfoModal: false });

      wx.showToast({
        title: '设置成功',
        icon: 'success',
        duration: 1000
      });

      // 跳转到首页
      this.navigateToIndex();
    } catch (err) {
      wx.hideLoading();
      console.error('更新用户信息失败', err);
      wx.showToast({
        title: err.message || '保存失败，请稍后重试',
        icon: 'none'
      });
    }
  },

  // 跳过用户信息设置
  onSkipUserInfo() {
    this.setData({ showUserInfoModal: false });
    wx.showToast({
      title: '登录成功',
      icon: 'success',
      duration: 1000
    });
    this.navigateToIndex();
  },

  // 跳转到首页
  navigateToIndex() {
    console.log('navigateToIndex被调用');
    setTimeout(() => {
      wx.reLaunch({
        url: '/pages/index/index',
        success: () => {
          console.log('reLaunch成功');
        },
        fail: (err) => {
          console.error('reLaunch失败:', err);
          wx.switchTab({
            url: '/pages/index/index',
            fail: (err2) => {
              console.error('switchTab也失败:', err2);
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
  },

  // 查看用户协议
  onViewAgreement() {
    wx.navigateTo({
      url: '/pages/agreement/agreement?type=user'
    });
  },

  // 查看隐私政策
  onViewPrivacy() {
    wx.navigateTo({
      url: '/pages/agreement/agreement?type=privacy'
    });
  }
});
