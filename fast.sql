-- ----------------------------
-- Table structure for menu
-- ----------------------------
DROP TABLE IF EXISTS `menu`;
CREATE TABLE `menu`  (
  `menu_id` int NOT NULL AUTO_INCREMENT COMMENT 'Menu ID',
  `menu_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'Menu name',
  `parent_id` int NULL DEFAULT 0 COMMENT 'Parent menu ID',
  `menu_sort` int NOT NULL COMMENT 'Menu order',
  `path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT 'Route path',
  `component` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT 'Component path',
  `menu_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'Menu type (M for directory, C for menu item)',
  `icon` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT 'Menu icon',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  PRIMARY KEY (`menu_id`) USING BTREE,
  UNIQUE INDEX `menu_id`(`menu_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 28 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = 'Menu' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of menu
-- Seed these five menus for Home and System Management.
-- Feature modules add their menus when their pages are available. Menus drive dynamic routes.
-- ----------------------------
INSERT INTO `menu` VALUES (1, 'System Management', 0, 99, 'system', NULL, 'M', 'system-management', '2026-01-25 17:48:15');
INSERT INTO `menu` VALUES (2, 'User Management', 1, 1, 'users', 'system/user/index', 'C', 'user-management', '2026-01-25 17:48:16');
INSERT INTO `menu` VALUES (3, 'Role Management', 1, 2, 'role', 'system/role/index', 'C', 'role-management', '2026-01-26 17:23:54');
INSERT INTO `menu` VALUES (4, 'Menu Management', 1, 3, 'menu', 'system/menu/index', 'C', 'menu-management', '2026-01-26 17:25:07');
INSERT INTO `menu` VALUES (5, 'Home', 0, 1, 'index', 'system/index', 'C', 'home', '2026-01-28 20:01:23');

-- ----------------------------
-- Table structure for role
-- ----------------------------
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role`  (
  `role_id` int NOT NULL AUTO_INCREMENT COMMENT 'Role ID',
  `role_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'Role name',
  `role_sort` int NOT NULL COMMENT 'Display order',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT '' COMMENT 'Notes',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  PRIMARY KEY (`role_id`) USING BTREE,
  UNIQUE INDEX `role_id`(`role_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = 'Role' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of role
-- Four roles: 1 super administrator, 2 regular user, 3 gaming companion and 4 customer support
-- ----------------------------
INSERT INTO `role` VALUES (1, 'admin', 1, 'Super Administrator', '2026-01-22 17:41:30');
INSERT INTO `role` VALUES (2, 'user', 2, 'Regular User', '2026-01-22 17:41:49');
INSERT INTO `role` VALUES (3, 'companion', 3, 'Gaming Companion', '2026-10-18 15:02:30');
INSERT INTO `role` VALUES (4, 'service', 4, 'Customer Support', '2026-10-19 10:00:00');

-- ----------------------------
-- Table structure for role_menu
-- ----------------------------
DROP TABLE IF EXISTS `role_menu`;
CREATE TABLE `role_menu`  (
  `role_id` int NOT NULL COMMENT 'Role ID',
  `menu_id` int NOT NULL COMMENT 'Menu ID',
  INDEX `fk_role_menu_role`(`role_id` ASC) USING BTREE,
  INDEX `fk_role_menu_menu`(`menu_id` ASC) USING BTREE,
  CONSTRAINT `fk_role_menu_menu` FOREIGN KEY (`menu_id`) REFERENCES `menu` (`menu_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_role_menu_role` FOREIGN KEY (`role_id`) REFERENCES `role` (`role_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = 'Role-menu association' ROW_FORMAT = DYNAMIC;

-- Leave role_menu empty because administrators already have access to every menu.
-- Feature modules will add menu permissions for gaming companions and customer support.

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `user_id` int NOT NULL AUTO_INCREMENT COMMENT 'User ID',
  `user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'Username',
  `sex` int NULL DEFAULT NULL COMMENT 'Gender (0 male, 1 female)',
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT 'Avatar',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'Password',
  `role_id` int NOT NULL DEFAULT 2 COMMENT 'Role ID',
  `balance` int NOT NULL DEFAULT 0 COMMENT 'Wallet balance (yuan)',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  UNIQUE INDEX `uk_user_name`(`user_name` ASC) USING BTREE,
  INDEX `fk_user_role`(`role_id` ASC) USING BTREE,
  CONSTRAINT `fk_user_role` FOREIGN KEY (`role_id`) REFERENCES `role` (`role_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 67 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = 'User' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user
-- Seed account 1 is admin, 2 is Zhang San, 3–34 are gaming companions and 66 is Official Support. Each seed account receives a random initial password.
-- Runtime avatar uploads are outside the sample files. The UI displays default avatars when an avatar file is unavailable.
-- ----------------------------
INSERT INTO `user` VALUES (1, 'admin', 0, NULL, HEX(RANDOM_BYTES(32)), 1, 0, '2026-01-14 11:29:43');
INSERT INTO `user` VALUES (2, 'Zhang San', NULL, NULL, HEX(RANDOM_BYTES(32)), 2, 868, '2026-10-17 13:26:32');
INSERT INTO `user` VALUES (3, 'Soft Bunny', 1, '/profile/upload/da3b2987a4b14e0ebe4f19464687ddd2_%E9%99%AA%E7%8E%A9%E5%A5%B31.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (4, 'North of the City', 0, '/profile/upload/77c4e766d8f34a09b24b711dee7261e3_%E7%94%B7%E9%99%AA%E7%8E%A91.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (5, 'Sweet Candy', 1, '/profile/upload/4a37c8e6d8344fd8bc089d305344ba3d_%E9%99%AA%E7%8E%A9%E5%A5%B32.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (6, 'Mountain Mist', 0, '/profile/upload/be488e797d884ffbba7a74096d18dc23_%E7%94%B7%E9%99%AA%E7%8E%A92.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (7, 'Fluttering Deer', 1, '/profile/upload/6b5dbe0b880a415e888170f628fa4b0e_%E9%99%AA%E7%8E%A9%E5%A5%B33.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (8, 'Lone Wolf', 0, '/profile/upload/860535a4c43146ca9483e2c06184141b_%E7%94%B7%E9%99%AA%E7%8E%A93.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (9, 'Mochi Cat', 1, '/profile/upload/4c0f0c807ab24dd199e43998b462d0e4_%E9%99%AA%E7%8E%A9%E5%A5%B34.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (10, 'Old Bai', 0, '/profile/upload/3734b16b6b1f458aa1ec2ab5c6d79cd9_%E7%94%B7%E9%99%AA%E7%8E%A94.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (11, 'Evening Breeze', 1, '/profile/upload/ae6d8a4e112142bd8f435546ca1c3246_%E9%99%AA%E7%8E%A9%E5%A5%B35.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (12, 'Passing Rain', 0, '/profile/upload/e7576bf256954c8fb8264928a3ab4c76_%E7%94%B7%E9%99%AA%E7%8E%A95.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (13, 'Chestnut', 1, '/profile/upload/b26fc02ec8524c47aebee44c42cfbc86_%E9%99%AA%E7%8E%A9%E5%A5%B36.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (14, 'A Che', 0, '/profile/upload/c0a5f796b0bf46b1ba6bf2112574574d_%E7%94%B7%E9%99%AA%E7%8E%A96.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (15, 'A Xiu', 0, '/profile/upload/bb83649891e14076a1bef5cbc8f7e64b_%E7%94%B7%E9%99%AA%E7%8E%A97.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (16, 'Peach Oolong', 1, '/profile/upload/813e32b2256d4f4b9e165fb426ec6fe6_%E9%99%AA%E7%8E%A9%E5%A5%B37.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (17, 'Oliver Twist', 0, '/profile/upload/f28d7549e6204ba48217ea58464bd6bc_%E7%94%B7%E9%99%AA%E7%8E%A98.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (18, 'Gardenia', 1, '/profile/upload/36c280c1cd034e5cbc1b7451824d00d1_%E9%99%AA%E7%8E%A9%E5%A5%B38.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (19, 'Deep White', 0, '/profile/upload/b0ee022c2e2b4004818afead3e1ad424_%E7%94%B7%E9%99%AA%E7%8E%A99.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (20, 'Kitten', 1, '/profile/upload/020fcd88cd94481e934a129a7998e25a_%E9%99%AA%E7%8E%A9%E5%A5%B39.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (21, 'Dried Fish', 0, '/profile/upload/0f3145cb745a40ccbd8f24c89e916544_%E7%94%B7%E9%99%AA%E7%8E%A910.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (22, 'Ban Xia', 1, '/profile/upload/7f9da81423b04b488424e32a7c0f8463_%E9%99%AA%E7%8E%A9%E5%A5%B310.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (23, 'Quiet Joy', 1, '/profile/upload/d153c4e817cd453dabc4bc87fa06600c_%E9%99%AA%E7%8E%A9%E5%A5%B311.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (24, 'Rice Mochi', 1, '/profile/upload/950bd1fb554847a59c0035f98367dbe2_%E9%99%AA%E7%8E%A9%E5%A5%B312.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (25, 'Mu Yan', 0, '/profile/upload/f84d4407cd4549f9ad99314b7f365b7d_%E7%94%B7%E9%99%AA%E7%8E%A911.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (26, 'Robin', 1, '/profile/upload/6ddc621b6f32496a86c8656e460834a0_%E9%99%AA%E7%8E%A9%E5%A5%B313.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (27, 'Lime', 1, '/profile/upload/7c150ebab52341d2917a5283c1a47891_%E9%99%AA%E7%8E%A9%E5%A5%B314.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (28, 'Mint Candy', 1, '/profile/upload/bdd572efde4d40378c2de119e0858f59_%E9%99%AA%E7%8E%A9%E5%A5%B315.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (29, 'Qing Ye', 0, '/profile/upload/8f9a34bccf6141afb3153de8dcfd48c8_%E7%94%B7%E9%99%AA%E7%8E%A912.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (30, 'Lychee', 1, '/profile/upload/3fdd7c15cc304f43b81791d37bb1654c_%E9%99%AA%E7%8E%A9%E5%A5%B316.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (31, 'Camellia', 1, '/profile/upload/0271dafc50c34f4c922d0fa495efff9c_%E9%99%AA%E7%8E%A9%E5%A5%B317.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (32, 'Malt Candy', 1, '/profile/upload/47ef03369a544999825990b4c8fab4c4_%E9%99%AA%E7%8E%A9%E5%A5%B318.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (33, 'Nineteen', 0, '/profile/upload/418088101aec4c66b00720e704ee6694_%E7%94%B7%E9%99%AA%E7%8E%A913.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (34, 'Jiang Ye', 0, '/profile/upload/61e761e4ecba4db080b85ef6f8ec669c_%E7%94%B7%E9%99%AA%E7%8E%A914.jpg', HEX(RANDOM_BYTES(32)), 3, 0, '2026-10-18 14:59:42');
INSERT INTO `user` VALUES (66, 'Official Support', NULL, NULL, HEX(RANDOM_BYTES(32)), 4, 0, '2026-10-19 10:00:00');

SET FOREIGN_KEY_CHECKS = 1;