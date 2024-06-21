-- 帮我写一个 postgresql 的建表语句。表示一个游戏资源的表 3d_assests 字段有,id,title,file_path,web_url,software,file_type,note,keywords,tags,meta,score,ctime，
-- 其中 id 递增，title 是字符串，file_path 文件路径，web_url  网络url, software 是字符串数组，file_type 是字符串，keywords 是 字符串数组，tags 也是， meta 是 jsonb类型，score 是小数，ctime 是创建时间

CREATE TABLE game_assets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    file_path TEXT,
    web_url TEXT,
    software VARCHAR(100)[],
    file_type VARCHAR(255),
    note TEXT,
    keywords VARCHAR(100)[],
    tags VARCHAR(100)[],
    meta JSONB,
    score DECIMAL(10, 2),
    ctime TIMESTAMP WITHOUT TIME ZONE
);

-- 单列索引
CREATE INDEX idx_title ON game_assets (title);
CREATE INDEX idx_file_path ON game_assets (file_path);
CREATE INDEX idx_web_url ON game_assets (web_url);
CREATE INDEX idx_file_type ON game_assets (file_type);

-- GIN 索引
CREATE INDEX idx_software ON game_assets USING GIN (software);
CREATE INDEX idx_keywords ON game_assets USING GIN (keywords);
CREATE INDEX idx_tags ON game_assets USING GIN (tags);
CREATE INDEX idx_meta ON game_assets USING GIN (meta);

-- B树索引
CREATE INDEX idx_score ON game_assets (score);
CREATE INDEX idx_ctime ON game_assets (ctime);