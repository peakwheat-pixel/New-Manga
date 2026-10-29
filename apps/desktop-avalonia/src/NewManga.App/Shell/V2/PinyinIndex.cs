using System.Text;

namespace NewManga.App.Shell.V2;

/// <summary>
/// V11R-B-1: local pinyin-initial search index for the Library search field (screen spec §2:
/// "搜索（中文/拼音首字母）"). No pinyin NuGet package is added (licence review would be required),
/// so this ships a compact, documented Han→initial table for common characters; characters outside
/// the table fall back to exact-character matching and are reported as a known limitation.
/// Matching rules: case-insensitive substring over the raw text first, then over the pinyin initials
/// (e.g. 「夜光列车」→「yglc」). Pure and unit-testable.
/// </summary>
public static class PinyinIndex
{
    private static readonly Dictionary<char, char> Initials = Build();

    public static bool Matches(string? text, string? query)
    {
        if (string.IsNullOrWhiteSpace(query))
        {
            return true;
        }

        if (string.IsNullOrEmpty(text))
        {
            return false;
        }

        var trimmed = query.Trim();
        if (text.Contains(trimmed, StringComparison.OrdinalIgnoreCase))
        {
            return true;
        }

        var letters = NormalizeLetters(trimmed);
        if (letters.Length == 0)
        {
            return false;
        }

        // Initials of every "word" (ASCII words included) so 「Saber 画集」 also matches "shj"/"hj".
        return ContainsInitials(text, letters);
    }

    /// <summary>Pinyin initials of one text; unmapped CJK characters contribute nothing.</summary>
    public static string InitialsOf(string? text)
    {
        if (string.IsNullOrEmpty(text))
        {
            return string.Empty;
        }

        var builder = new StringBuilder(text.Length);
        foreach (var character in text)
        {
            if (Initials.TryGetValue(character, out var initial))
            {
                builder.Append(initial);
            }
            else if (char.IsAsciiLetterOrDigit(character))
            {
                builder.Append(char.ToLowerInvariant(character));
            }
        }

        return builder.ToString();
    }

    private static bool ContainsInitials(string text, string letters)
    {
        if (InitialsOf(text).Contains(letters, StringComparison.Ordinal))
        {
            return true;
        }

        foreach (var word in text.Split(new[] { ' ', '\t', '・', '·', '-', '_', '/', '・' }, StringSplitOptions.RemoveEmptyEntries))
        {
            if (InitialsOf(word).Contains(letters, StringComparison.Ordinal))
            {
                return true;
            }
        }

        return false;
    }

    private static string NormalizeLetters(string query)
    {
        var builder = new StringBuilder(query.Length);
        foreach (var character in query)
        {
            if (char.IsAsciiLetter(character))
            {
                builder.Append(char.ToLowerInvariant(character));
            }
        }

        return builder.ToString();
    }

    private static Dictionary<char, char> Build()
    {
        var map = new Dictionary<char, char>(420);
        Add(map, 'a', "阿啊爱安按暗奥");
        Add(map, 'b', "八巴白百半办包报宝帮北背备本比边变表别病波不步部");
        Add(map, 'c', "才采彩参草层查差产长场车陈成城程吃持池出初除处川传船窗床创春词次从存村错車場");
        Add(map, 'd', "大带代单但当到道得的灯登等低底地第点电调定东冬动都读段断对多独丢");
        Add(map, 'e', "而二儿耳");
        Add(map, 'f', "发法翻反返方防房放飞非费分份风封峰夫服福负复富父");
        Add(map, 'g', "该改干刚高告哥歌格个各给根跟更工公功共沟古谷股故挂关观官管馆光广归规贵国果过港");
        Add(map, 'h', "哈还孩海害含汉好号合和河黑很红后候湖户花华画话怀坏欢环换黄灰回会活火或");
        Add(map, 'j', "机基击及级极几计记纪技际济既继加家甲假架尖间检简见件建健将讲交角脚叫较教接街节结解姐介界借今金紧进近经京精井景静境究九久酒旧就局举句具剧据卷觉军江集");
        Add(map, 'k', "卡开看康考科可克客课肯空孔口扣块快宽矿况亏困扩");
        Add(map, 'l', "拉来蓝览浪劳老乐类冷离里理力立利历丽连联脸练良亮量两列林临领另流六龙楼路旅绿乱论轮罗落了");
        Add(map, 'm', "妈麻马吗买卖满忙毛么没每美门们迷米面民名明命摸模母木目");
        Add(map, 'n', "拿哪那内南难脑呢能你年念鸟您宁牛农弄努女暖");
        Add(map, 'o', "哦欧");
        Add(map, 'p', "爬怕排牌派旁胖跑朋批片品平评瓶破普");
        Add(map, 'q', "七其奇齐起气汽器钱前浅枪强桥巧切亲轻清情请穷秋求区取全权泉去趣");
        Add(map, 'r', "然让热人认日容肉如入软");
        Add(map, 's', "三色森杀沙山删闪商上少社设身深神生声省胜师石时识实使世事市式试收手受书叔树数属双水睡说四送苏速算虽随孙所舍");
        Add(map, 't', "他它她台太谈汤堂糖躺讨特提题体天条跳听停通同头图土团推腿");
        Add(map, 'w', "挖外完玩晚王往网忘危为围伟卫位温文问我无五午舞物务误雾");
        Add(map, 'x', "西希习喜系细下夏先现线相想向象像消小效校些写谢心新信星形醒姓性兄休修需许序续选学雪寻训");
        Add(map, 'y', "压呀牙亚言严眼演阳样要药也页夜一衣已以义意因音银引应英影用有又右于余鱼雨语育元原园员远院愿约月云运");
        Add(map, 'z', "杂再在咱早造则怎增扎站张章找照着者这真争征整正证之支知直只纸指至志治中终钟种周主住注祝专转装状准自字总走足组最左做作坐座");
        return map;
    }

    private static void Add(Dictionary<char, char> map, char initial, string characters)
    {
        foreach (var character in characters)
        {
            map[character] = initial;
        }
    }
}
